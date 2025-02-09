"""Celery tasks for exporting data from the project."""
import json
import csv
import os
import shutil
import tempfile

import pandas as pd
from celery import shared_task
from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage

from twf.models import Project
from twf.tasks.task_base import get_project_and_user, start_task, end_task, update_task
from twf.utils.create_export_utils import create_data


@shared_task(bind=True)
def export_documents_task(self, project_id, user_id, export_single_file=True, export_type="documents"):
    try:
        project, user = get_project_and_user(project_id, user_id)
    except ValueError as e:
        raise ValueError(str(e)) from e

    docs_to_export = project.documents.all()
    number_of_docs = docs_to_export.count()

    task, percentage = start_task(
        self, project, user_id,
        title="Export Documents",
        description="Ongoing task",
        text="Starting Task",
        percentage_complete=0
    )

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
                    export_filepath = os.path.join(temp_dir, export_filename)
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

            processed_entries += 1
            update_task(self, task, f"Exporting {processed_entries}/{number_of_docs}", processed_entries, number_of_docs)

        # 3rd step: Store the final result
        if export_single_file:
            zip_filename = f"export_{project.id}.zip"
            zip_filepath = shutil.make_archive(zip_filename.replace(".zip", ""), "zip", temp_dir)
            result_filepath = zip_filepath
        else:
            export_filename = f"export_{project.id}.json"
            export_filepath = os.path.join(temp_dir, export_filename)
            with open(export_filepath, "w", encoding="utf8") as sf:
                json.dump(export_data_list, sf, indent=4)
            result_filepath = export_filepath

        # Move to a persistent storage location for download
        relative_export_path = f"exports/{os.path.basename(result_filepath)}"
        final_result_path = os.path.join(settings.MEDIA_ROOT, relative_export_path)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(final_result_path), exist_ok=True)

        with open(result_filepath, "rb") as f:
            saved_filename = default_storage.save(relative_export_path, File(f))

    finally:
        # Cleanup temporary files AFTER successful storage
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    # 4th step: End task and return the download URL
    download_url = f"{settings.MEDIA_URL}{saved_filename}"
    end_task(self, task, "Export Completed", description=f"{number_of_docs} documents exported.",
             meta={"download_url": download_url})

    return {"download_url": download_url}


@shared_task(bind=True)
def export_collections_task(self, project_id, user_id):
    try:
        project, user = get_project_and_user(project_id, user_id)
    except ValueError as e:
        raise ValueError(str(e)) from e

    collection_id = None
    export_single_file = True


@shared_task(bind=True)
def export_project_task(self, project_id, user_id):
    try:
        project, user = get_project_and_user(project_id, user_id)
    except ValueError as e:
        raise ValueError(str(e)) from e

    export_type = 'sql' # Can be 'sql' or 'json'


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
