"""Celery tasks for extracting Transkribus export files."""
import logging
import os
import zipfile

from celery import shared_task
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from simple_alto_parser import PageFileParser

from twf.models import Project, User, Document, Page
from twf.page_file_meta_data_reader import extract_transkribus_file_metadata
from twf.tasks.task_base import start_task, update_task_percentage, end_task, fail_task
from twf.utils.file_utils import delete_all_in_folder


@shared_task(bind=True)
def extract_zip_export_task(self, project_id, user_id):
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
                    new_copied_filename = f"{project.collection_id}_{data['docId']}_{data['pageId']}_{data['pageNr']}.xml"
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
                    task, percentage_complete = update_task_percentage(self, task, f'Processed {processed_documents} documents...',
                                                                       percentage_complete + percentage_of_extraction/3)

                else:
                    print("ERROR")  # TODO: Handle error

        # Delete all documents that were not in the export
        for doc_id in all_existing_documents:
            Document.objects.filter(project=project, document_id=doc_id).delete()

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
                 description=f'Transkribus Export Extraction for project "{project.title}". '
                             f'Extracted {total_files} files, created {created_documents} documents, '
                             f'processed and parsed {processed_pages} pages.')

        return {'status': 'completed'}

    except User.DoesNotExist as e:
        error_message = f"User with id {user_id} does not exist."
        fail_task(self, task, error_message)
        raise ValueError(error_message) from e
    except Exception as e:
        fail_task(self, task, str(e))
        raise ValueError(str(e)) from e
