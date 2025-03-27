"""Celery tasks for exporting data from the project."""
import json
import csv
import os
import shutil
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
from celery import shared_task
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.serializers import serialize
from django.utils.text import slugify

from twf.models import Project, Export, Page, PageTag, CollectionItem, DictionaryEntry, Variation, DateVariation
from twf.tasks.task_base import BaseTWFTask
from twf.utils.create_export_utils import create_data


@shared_task(bind=True, base=BaseTWFTask)
def export_documents_task(self, project_id, user_id, **kwargs):
    print(kwargs)
    self.validate_task_parameters(kwargs, ['export_type', 'export_single_file'])

    docs_to_export = self.project.documents.all()
    self.set_total_items(docs_to_export.count())

    export_type = kwargs.get('export_type')
    export_single_file = kwargs.get('export_single_file')

    # 1st step: Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    try:
        # 2nd step: Export documents
        processed_entries = 0
        export_data_list = []

        for doc in docs_to_export:
            if export_type == "documents":
                export_doc_data = create_data(doc)

                if export_single_file:
                    export_filename = f"document_{doc.document_id}.json"
                    export_filepath = Path(temp_dir) / export_filename
                    with open(export_filepath, "w", encoding="utf8") as sf:
                        json.dump(export_doc_data, sf, indent=4)
                else:
                    export_data_list.append(export_doc_data)

            elif export_type == "pages":
                for page in doc.pages.all():
                    export_page_data = create_data(page)

                    if export_single_file:
                        export_filename = f"page_{page.tk_page_id}.json"
                        export_filepath = os.path.join(temp_dir, export_filename)
                        with open(export_filepath, "w", encoding="utf8") as sf:
                            json.dump(export_page_data, sf, indent=4)
                    else:
                        export_data_list.append(export_page_data)

            self.advance_task()

        # 3rd step: Store the final result
        if export_single_file:
            zip_filename = f"export_{self.project.id}.zip"
            zip_filepath = shutil.make_archive(zip_filename.replace(".zip", ""), "zip", temp_dir)
            result_filepath = zip_filepath
        else:
            export_filename = f"export_{self.project.id}.json"
            export_filepath = Path(temp_dir) / export_filename
            with open(export_filepath, "w", encoding="utf8") as sf:
                json.dump(export_data_list, sf, indent=4)
            result_filepath = export_filepath

        # Move to a persistent storage location for download
        result_filename = Path(result_filepath).name
        relative_export_path = f"exports/{result_filename}"
        final_result_path = Path(settings.MEDIA_ROOT) / relative_export_path

        # Ensure the directory exists
        final_result_path.parent.mkdir(parents=True, exist_ok=True)

        with open(result_filepath, "rb") as f:
            saved_filename = default_storage.save(relative_export_path, File(f))

    finally:
        # Cleanup temporary files AFTER successful storage
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


    export_instance = Export(
        project=self.project,
        export_file=saved_filename,  # Save the path to the file
        export_type=export_type
    )
    export_instance.save(current_user=self.user)

    # 4th step: End task and return the download URL
    download_url = export_instance.export_file.url
    self.end_task(download_url=download_url)


@shared_task(bind=True, base=BaseTWFTask)
def export_collections_task(self, project_id, user_id, **kwargs):

    collection_id = None
    export_single_file = True
    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def export_project_task(self, project_id, user_id, **kwargs):
    self.validate_task_parameters(kwargs,
                                  ['include_dictionaries', 'include_media_files'])
    include_dictionaries = kwargs.get("include_dictionaries", True)
    include_media_files = kwargs.get("include_media_files", True)

    project = self.project  # Provided by BaseTWFTask
    export_data = {}

    # Core data export
    export_data["project"] = serialize("json", [project])
    export_data["documents"] = serialize("json", project.documents.all())

    pages = Page.objects.filter(document__project=project).select_related("document")
    export_data["pages"] = serialize("json", pages)

    tags = PageTag.objects.filter(page__document__project=project)
    export_data["tags"] = serialize("json", tags)

    export_data["collections"] = serialize("json", project.collections.all())

    collection_items = CollectionItem.objects.filter(collection__project=project)
    export_data["collection_items"] = serialize("json", collection_items)

    export_data["prompts"] = serialize("json", project.prompts.all())

    export_data["workflows"] = serialize("json", project.workflow_set.all())

    if include_dictionaries:
        dictionaries = project.selected_dictionaries.all()
        entries = DictionaryEntry.objects.filter(dictionary__in=dictionaries)
        variations = Variation.objects.filter(entry__in=entries)
        date_variations = DateVariation.objects.all()

        export_data["dictionaries"] = serialize("json", dictionaries)
        export_data["dictionary_entries"] = serialize("json", entries)
        export_data["variations"] = serialize("json", variations)
        export_data["date_variations"] = serialize("json", date_variations)

    # Create ZIP
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # JSON files
        for name, content in export_data.items():
            zip_file.writestr(f"{name}.json", content)

        # Media files: downloaded ZIP and page XMLs
        if include_media_files:
            if project.downloaded_zip_file:
                zip_file.writestr(f"media/{os.path.basename(project.downloaded_zip_file.name)}",
                                  project.downloaded_zip_file.read())

            for page in pages:
                if page.xml_file and page.xml_file.name:
                    try:
                        zip_file.writestr(f"media/{os.path.basename(page.xml_file.name)}",
                                          page.xml_file.read())
                    except Exception as e:
                        pass  # Log this if needed

    # Save the file in an Export object
    export_filename = f"{slugify(project.title)}-export.zip"
    export_file = ContentFile(zip_buffer.getvalue(), name=export_filename)
    export = Export(
        project=project,
        export_file=export_file,
        export_type="project",
        created_by=self.user,
        modified_by=self.user,
    )
    export.save(current_user=self.user)

    self.end_task(text="Export finished", status="SUCCESS",
                  download_url=export.export_file.url)




@shared_task(bind=True, base=BaseTWFTask)
def export_to_zenodo_task(self, project_id, user_id, **kwargs):

    export_type = 'sql' # Can be 'sql' or 'json'
    self.end_task()


def export_data_task(self, project_id, export_type, export_format, schema):
    """Export data from a project.
    :param self: Celery task
    :param project_id: Project ID
    :param export_type: Type of data to export (documents or collections)
    :param export_format: Format of the export (json, csv, excel)
    :param schema: Optional schema for filtering the data
    :return: Exported data in the specified format"""

    try:
        # Fetch the project
        project = Project.objects.get(id=project_id)
        data = []

        # Retrieve documents or collections based on export_type
        if export_type == 'documents':
            data = project.documents.all()
        elif export_type == 'collections':
            data = project.collections.all()

        # Apply schema if provided (optional filtering)
        if schema:
            schema_fields = json.loads(schema)
            data = filter_data_by_schema(data, schema_fields)

        # Export based on format
        if export_format == 'json':
            return generate_json(data)
        elif export_format == 'csv':
            return generate_csv(data)
        elif export_format == 'excel':
            return generate_excel(data)

    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


def filter_data_by_schema(data, schema_fields):
    """Filter data based on the provided schema fields (attributes) of the model.
    :param data: Data to filter
    :param schema_fields: Fields to include in the filtered data
    :return: Filtered data"""
    # This function filters the data based on the provided schema
    filtered_data = []
    for item in data:
        filtered_item = {field: getattr(item, field, '') for field in schema_fields}
        filtered_data.append(filtered_item)
    return filtered_data


def generate_json(data):
    """Convert data to JSON string
    :param data: Data to export
    :return: JSON string"""
    return json.dumps([item.to_dict() for item in data], indent=4)


def generate_csv(data):
    """Convert data to CSV string
    :param data: Data to export
    :return: CSV string"""
    output = []
    fieldnames = data[0].keys() if data else []

    csv_output = csv.DictWriter(output, fieldnames=fieldnames)
    csv_output.writeheader()
    for row in data:
        csv_output.writerow(row)

    return ''.join(output)


def generate_excel(data):
    """Convert data to Excel file
    :param data: Data to export
    :return: Excel file"""
    df = pd.DataFrame(data)
    output = df.to_excel(index=False)
    return output
