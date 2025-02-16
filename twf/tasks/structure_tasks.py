"""Celery tasks for extracting Transkribus export files."""
import logging
import os
import uuid
import zipfile

from celery import shared_task
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from simple_alto_parser import PageFileParser

from twf.models import Document, Page
from twf.utils.page_file_meta_data_reader import extract_transkribus_file_metadata
from twf.tasks.task_base import BaseTWFTask
from twf.utils.file_utils import delete_all_in_folder


@shared_task(bind=True, base=BaseTWFTask)
def extract_zip_export_task(self, project_id, user_id, **kwargs):
    """Extract the Transkribus export zip file and create Document and Page instances."""

    try:

        # Step 1: Validate and prepare the zip file
        zip_file, extract_to_path = prepare_zip_file(self.project, self)

        # Step 2: Extract files from the zip archive
        copied_files = extract_files_from_zip(zip_file, extract_to_path, self.project, self)

        # Step 3: Process extracted files and create/update Document and Page instances
        process_extracted_files(copied_files, self.project, self.user, self)

        # Step 4: Parse page data
        parse_pages(self.project, self.user, self)

        # Finalize the task
        self.end_task()

        return {'status': 'completed'}

    except Exception as e:
        self.end_task(status="FAILURE")


def prepare_zip_file(project, celery_task):
    """Check the zip file and prepare the extraction path."""
    zip_file = project.downloaded_zip_file
    if not zip_file or not os.path.exists(zip_file.path):
        error_message = "The zip file does not exist in the file system."
        raise ValueError(error_message)

    fs = FileSystemStorage()
    extract_to_path = fs.path(f"transkribus_exports/{project.collection_id}/")
    if not fs.exists(extract_to_path):
        os.makedirs(extract_to_path)
    delete_all_in_folder(extract_to_path)

    celery_task.update_progress(2)
    return zip_file, extract_to_path


def extract_files_from_zip(zip_file, extract_to_path, project, celery_task):
    """Extract valid files from the zip archive."""
    copied_files = []
    with zipfile.ZipFile(zip_file.path, 'r') as zip_ref:
        valid_files = [
            x for x in zip_ref.infolist()
            if ("/page/" in x.filename and x.filename.endswith(".xml"))
            or x.filename.endswith('metadata.xml') or x.filename.endswith('mets.xml')
        ]
        total_files = len(valid_files)

        for i, file_info in enumerate(valid_files, start=1):
            with zip_ref.open(file_info) as file_data:
                new_filename = generate_new_filename(file_info, project)
                new_filepath = os.path.join(extract_to_path, new_filename)
                with open(new_filepath, 'wb') as new_file:
                    new_file.write(file_data.read())
                    copied_files.append(new_filepath)

                # Update progress
                progress = (i / total_files) * 30  # Allocate 30% for extraction
                celery_task.update_progress(2 + progress)
    return copied_files


def generate_new_filename(file_info, project):
    """Generate a new filename for extracted files."""
    if file_info.filename.endswith(('metadata.xml', 'mets.xml')):
        return f"{file_info.filename.split('/')[0]}_{file_info.filename.split('/')[-1]}"
    else:
        return f"{project.collection_id}_{uuid.uuid4().hex}.xml"


def process_extracted_files(copied_files, project, extracting_user, celery_task):
    """Process extracted files and create/update Document and Page instances."""
    all_existing_documents = set(Document.objects.filter(project=project).values_list('document_id', flat=True))
    total_files = len(copied_files)
    for i, file in enumerate(copied_files, start=1):
        if not file.endswith(('metadata.xml', 'mets.xml')):
            try:
                data = extract_transkribus_file_metadata(file)
                handle_document_and_page(data, file, project, extracting_user, all_existing_documents)
            except Exception as e:
                logging.warning(f"Failed to process file {file}: {e}")
        progress = (i / total_files) * 30  # Allocate another 30% for processing
        celery_task.update_progress(32 + progress)


def handle_document_and_page(data, file, project, extracting_user, existing_documents):
    """Handle creation/updating of Document and Page instances."""
    doc_instance, _ = Document.objects.get_or_create(
        project=project,
        document_id=data['docId'],
        defaults={'created_by': extracting_user, 'modified_by': extracting_user}
    )
    existing_documents.discard(doc_instance.document_id)

    page_instance, _ = Page.objects.get_or_create(
        document=doc_instance,
        tk_page_id=data['pageId'],
        tk_page_number=data['pageNr'],
        defaults={'created_by': extracting_user, 'modified_by': extracting_user}
    )
    page_instance.xml_file.name = file
    page_instance.save(current_user=extracting_user)


def parse_pages(project, extracting_user, celery_task):
    """Parse pages and extract data."""
    all_pages = Page.objects.filter(document__project=project).order_by('document__document_id', 'tk_page_number')
    total_pages = all_pages.count()

    for i, page in enumerate(all_pages, start=1):
        page_parser = PageFileParser(parser_config={
            'line_type': 'TextRegion',
            'logging': {'level': logging.WARN},
            'export': {'json': {'print_files': True, 'print_filename': True, 'print_file_meta_data': True}}
        })
        page_parser.add_file(page.xml_file.path)
        page_parser.parse()
        page.parsed_data = page_parser.get_alto_files()[0].get_standalone_json_object()
        page.last_parsed_at = timezone.now()
        page.save(current_user=extracting_user)

        progress = (i / total_pages) * 30  # Allocate last 30% for parsing
        celery_task.update_progress(66 + progress)


