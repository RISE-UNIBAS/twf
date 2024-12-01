"""Celery tasks for extracting Transkribus export files."""
import logging
import os
import uuid
import zipfile

from celery import shared_task
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from simple_alto_parser import PageFileParser

from twf.models import Project, User, Document, Page
from twf.utils.page_file_meta_data_reader import extract_transkribus_file_metadata
from twf.tasks.task_base import start_task, update_task_percentage, end_task, fail_task
from twf.utils.file_utils import delete_all_in_folder


@shared_task(bind=True)
def extract_zip_export_task(self, project_id, user_id):
    """Extract the Transkribus export zip file and create Document and Page instances."""

    try:
        project, extracting_user, task = initialize_task(self, project_id, user_id)

        # Step 1: Validate and prepare the zip file
        zip_file, extract_to_path = prepare_zip_file(project, task)

        # Step 2: Extract files from the zip archive
        copied_files = extract_files_from_zip(zip_file, extract_to_path, project, task)

        # Step 3: Process extracted files and create/update Document and Page instances
        process_extracted_files(copied_files, project, extracting_user, task)

        # Step 4: Parse page data
        parse_pages(project, extracting_user, task)

        # Finalize the task
        finalize_task(task, project, copied_files)

        return {'status': 'completed'}

    except Exception as e:
        handle_task_failure(self, task, str(e), e)
        raise


def initialize_task(self, project_id, user_id):
    """Initialize task and validate project and user."""
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise ValueError(f"Project with id {project_id} does not exist.")

    try:
        extracting_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise ValueError(f"User with id {user_id} does not exist.")

    task, _ = start_task(self, project, user_id,
                         text="Starting Transkribus Export Extraction...",
                         title="Transkribus Export Extraction")
    return project, extracting_user, task


def prepare_zip_file(project, task):
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

    update_task_percentage(task, "Preparing extraction...", 2)
    return zip_file, extract_to_path


def extract_files_from_zip(zip_file, extract_to_path, project, task):
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
                update_task_percentage(task, f"Extracted {i}/{total_files} files...", 2 + progress)
    return copied_files


def generate_new_filename(file_info, project):
    """Generate a new filename for extracted files."""
    if file_info.filename.endswith(('metadata.xml', 'mets.xml')):
        return f"{file_info.filename.split('/')[0]}_{file_info.filename.split('/')[-1]}"
    else:
        return f"{project.collection_id}_{uuid.uuid4().hex}.xml"


def process_extracted_files(copied_files, project, extracting_user, task):
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
        update_task_percentage(task, f"Processed {i}/{total_files} files...", 32 + progress)


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


def parse_pages(project, extracting_user, task):
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
        update_task_percentage(task, f"Parsed {i}/{total_pages} pages...", 66 + progress)


def finalize_task(task, project, copied_files):
    """Finalize the task with completion status."""
    end_task(task, "Transkribus Export Extraction Completed.",
             description=f'Transkribus Export Extraction for project "{project.title}".',
             meta={"total_files": len(copied_files)})


def handle_task_failure(self, task, error_message, exc):
    """Handle task failure by updating its status."""
    if task:
        fail_task(self, task, f"Task failed: {str(exc)}", exception=exc)


def update_task_percentage(task, text, percentage):
    """Update the task's percentage and text."""
    task.text = text
    task.percentage = percentage
    task.save()
    return task, percentage


#shared_task(bind=True)
def legacy_extract_zip_export_task(self, project_id, user_id):
    """Extract the Transkribus export zip file and create Document and Page instances.
    :param self: Celery task
    :param project_id: Project ID
    :param user_id: User ID"""

    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist as e:
        error_message = f"Project with id {project_id} does not exist."
        raise ValueError(error_message) from e

    task, percentage_complete = start_task(self, project, user_id, text="Starting Transkribus Export Extraction...",
                                           title="Transkribus Export Extraction")

    try:
        extracting_user = User.objects.get(pk=user_id)
        zip_file = project.downloaded_zip_file

        # Check if the zip file exists in the file system
        if not zip_file:
            error_message = "No zip file found in the project."
            fail_task(self, task, error_message)
            raise ValueError(error_message)

        if not os.path.exists(zip_file.path):
            error_message = "The zip file does not exist in the file system."
            fail_task(self, task, error_message)
            raise ValueError(error_message)

        fs = FileSystemStorage()

        # Get the path to save the extracted files to
        extract_to_path = fs.path(f"transkribus_exports/{project.collection_id}/")
        if not fs.exists(extract_to_path):
            os.makedirs(extract_to_path)
        # Clear the folder before extracting
        delete_all_in_folder(extract_to_path)
        percentage_complete = 2
        task, percentage_complete = update_task_percentage(self, task, f'Preparing...',
                                                           percentage_complete)

        # Extract the zip file and search for page.xml files
        with zipfile.ZipFile(zip_file.path, 'r') as zip_ref:
            all_files_info = zip_ref.infolist()
            valid_files = [x for x in all_files_info if ("/page/" in x.filename and x.filename.endswith(".xml"))
                           or x.filename.endswith('metadata.xml') or x.filename.endswith('mets.xml')]

            total_files = len(valid_files)
            processed_files = 0
            percentage_complete = 3
            task, percentage_complete = update_task_percentage(self, task, f'Extracting {total_files} files...',
                                                               percentage_complete)

            # Save the extracted files to the folder
            unique_id = 1
            copied_files = []
            for file_info in valid_files:
                with zip_ref.open(file_info) as file_data:
                    if file_info.filename.endswith('metadata.xml') or file_info.filename.endswith('mets.xml'):
                        new_filename = file_info.filename.split("/")[0] + "_" + file_info.filename.split("/")[-1]
                        new_filepath = os.path.join(extract_to_path, new_filename)
                    else:
                        new_filename = f"{project.collection_id}_{unique_id:05}.xml"
                        new_filepath = os.path.join(extract_to_path, new_filename)

                    # Write the extracted data to a new file with the new filename
                    with open(new_filepath, 'wb') as new_file:
                        new_file.write(file_data.read())
                        copied_files.append(new_filepath)

                    unique_id += 1

                # Update Processing state
                processed_files += 1
                percentage_of_extraction = (processed_files / total_files) * 100
                task, percentage_complete = update_task_percentage(self, task, f'Extracted {processed_files} files...',
                                                                   percentage_complete + percentage_of_extraction/3)

        percentage_complete = 32
        task, percentage_complete = update_task_percentage(self, task, f'Extracted {total_files} files...',
                                                           percentage_complete)

        #############################
        # Process the extracted files
        # Document and Page instances are only created if they do not exist yet
        all_existing_documents = list(Document.objects.filter(project=project).values_list('document_id', flat=True))
        created_documents = 0
        processed_documents = 0

        for file in copied_files:
            if file.endswith('metadata.xml') or file.endswith('mets.xml'):
                pass
            else:
                # Read the file and extract the Transkribus metadata
                data = extract_transkribus_file_metadata(file)
                if "docId" in data and "pageId" in data and "pageNr" in data:
                    new_copied_filename = (f"{project.collection_id}_"
                                           f"{data['docId']}_{data['pageId']}_{data['pageNr']}.xml")
                    renamed_filepath = os.path.join(extract_to_path, new_copied_filename)
                    os.rename(file, renamed_filepath)

                    # Process the file
                    # # 1.) Get or create a document with the same ID
                    doc_instance, created = Document.objects.get_or_create(project=project,
                                                                           document_id=data['docId'],
                                                                           created_by=extracting_user,
                                                                           modified_by=extracting_user)
                    if created:
                        created_documents += 1

                    # remove document from existing documents list
                    if doc_instance.document_id in all_existing_documents:
                        all_existing_documents.remove(doc_instance.document_id)

                    # # 2.) Create a page instance
                    page_instance, created = Page.objects.get_or_create(document=doc_instance,
                                                                        tk_page_id=data['pageId'],
                                                                        tk_page_number=data['pageNr'],
                                                                        created_by=extracting_user,
                                                                        modified_by=extracting_user)
                    page_instance.xml_file.name = f"transkribus_exports/{project.collection_id}/{new_copied_filename}"
                    page_instance.save(current_user=extracting_user)

                    # Update Processing state
                    processed_documents += 1
                    percentage_of_extraction = (processed_documents / total_files) * 100
                    task, percentage_complete = update_task_percentage(self, task,
                                                                       f'Processed {processed_documents} documents...',
                                                                       percentage_complete + percentage_of_extraction/3)

                else:
                    print("ERROR")  # TODO: Handle error

        # Delete all documents that were not in the export
        deleted_documents = 0
        for doc_id in all_existing_documents:
            Document.objects.filter(project=project, document_id=doc_id).delete()
            deleted_documents += 1

        percentage_complete = 66
        task, percentage_complete = update_task_percentage(self, task, f'Processed {processed_documents} documents...',
                                                           percentage_complete)

        #############################
        # PARSE THE PAGES
        parser_config = {'line_type': 'TextRegion',
                         'logging': {'level': logging.WARN},
                         'export': {'json': {
                             'print_files': True,
                             'print_filename': True,
                             'print_file_meta_data': True,
                         }}}

        all_pages = Page.objects.filter(document__project=project).order_by('document__document_id', 'tk_page_number')
        total_pages = all_pages.count()
        processed_pages = 0

        for page in all_pages:
            parse_time = timezone.now()

            page_parser = PageFileParser(parser_config=parser_config)
            page_parser.add_file(page.xml_file.path)
            page_parser.parse()
            page.parsed_data = page_parser.get_alto_files()[0].get_standalone_json_object()
            page.last_parsed_at = parse_time
            page.save(current_user=extracting_user)

            # Update Processing state
            processed_pages += 1
            percentage_of_parsing = (processed_pages / total_pages) * 100
            task, percentage_complete = update_task_percentage(self, task, f'Parsed {processed_pages} pages...',
                                                               percentage_complete + percentage_of_parsing/3)

        end_task(self, task, 'Transkribus Export Extraction Completed.',
                 description=f'Transkribus Export Extraction for project "{project.title}".',
                 meta={
                     "total_files": total_files,
                     "processed_documents": processed_documents,
                     "created_documents": created_documents,
                     "deleted_documents": deleted_documents
                 })

        return {'status': 'completed'}

    except User.DoesNotExist as e:
        error_message = f"User with id {user_id} does not exist."
        fail_task(self, task, error_message)
        raise ValueError(error_message) from e
    except ValueError as e:
        fail_task(self, task, str(e))
        raise ValueError(str(e)) from e
    except Exception as e:
        fail_task(self, task, str(e))
        raise ValueError(str(e)) from e
