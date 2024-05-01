"""This module contains the functions for extracting page.xml files from a Transkribus export zip file. The extracted
files are then processed and saved to the database."""
import logging
import os
import time
import zipfile

from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from simple_alto_parser import PageFileParser

from main.models import Project, Document, Page
from main.page_file_meta_data_reader import extract_transkribus_file_metadata
from main.utils.file_utils import delete_all_in_folder
from main.views.views_ajax_base import set_progress, set_details, calculate_and_set_progress, add_details

PROGRESS_JOB_NAME = "extract-progress"
DETAIL_JOB_NAME = "extract-progress-detail"


async def start_extraction(request, project_id):
    """This function starts the extraction process."""
    set_progress(0, project_id, PROGRESS_JOB_NAME)
    extract_zip_export_async = sync_to_async(extract_zip_export, thread_sensitive=True)
    await extract_zip_export_async(project_id, request.user)
    return JsonResponse({'status': 'success'}, status=200)


def extract_zip_export(project_id, extracting_user):
    """This function extracts page.xml files from a Transkribus export zip file. It then processes the extracted files
    and renames them according to the Transkribus document and page IDs. The extracted files are saved in a folder
    named after the collection ID of the project."""

    try:
        # Get the projects to save the documents to
        project = Project.objects.get(pk=project_id)
        zip_file = project.downloaded_zip_file
        fs = FileSystemStorage()

        # Get the path to save the extracted files to
        extract_to_path = fs.path(f"transkribus_exports/{project.collection_id}/")
        if not fs.exists(extract_to_path):
            os.makedirs(extract_to_path)
        # Clear the folder before extracting
        delete_all_in_folder(extract_to_path)

        # Extract the zip file and search for page.xml files
        with zipfile.ZipFile(zip_file.path, 'r') as zip_ref:
            all_files_info = zip_ref.infolist()
            valid_files = [x for x in all_files_info if "/page/" in x.filename and x.filename.endswith(".xml")]

            total_files = len(valid_files)
            total_steps = total_files * 3
            processed_steps = 0

            # Save the extracted files to the folder
            unique_id = 1
            copied_files = []
            set_details(f"Extracting {total_files} files.", project_id, DETAIL_JOB_NAME)
            for file_info in valid_files:
                with zip_ref.open(file_info) as file_data:

                    new_filename = f"{project.collection_id}_{unique_id:05}.xml"
                    new_filepath = os.path.join(extract_to_path, new_filename)

                    # Write the extracted data to a new file with the new filename
                    with open(new_filepath, 'wb') as new_file:
                        new_file.write(file_data.read())
                        copied_files.append(new_filepath)

                    unique_id += 1

                # Update Processing state
                processed_steps += 1
                calculate_and_set_progress(processed_steps, total_steps, project_id, PROGRESS_JOB_NAME)
                add_details(f"Extracted file {new_filename}.", project_id, DETAIL_JOB_NAME)

        #############################
        # Process the extracted files
        created_documents = 0
        add_details(f"Processing {len(copied_files)} files.", project_id, DETAIL_JOB_NAME)
        for file in copied_files:
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

                # # 2.) Create a page instance
                page_instance, created = Page.objects.get_or_create(document=doc_instance,
                                                                    tk_page_id=data['pageId'],
                                                                    tk_page_number=data['pageNr'],
                                                                    created_by=extracting_user,
                                                                    modified_by=extracting_user)
                page_instance.xml_file.name = f"transkribus_exports/{project.collection_id}/{new_copied_filename}"
                page_instance.save(current_user=extracting_user)

                # Update Processing state
                processed_steps += 1
                calculate_and_set_progress(processed_steps, total_steps, project_id, PROGRESS_JOB_NAME)
                add_details(f"Processed Page {page_instance.tk_page_id}", project_id, DETAIL_JOB_NAME)

            else:
                print("ERROR")  # TODO: Handle error

        parser_config = {'line_type': 'TextRegion', 'logging': {'level': logging.WARN}}

        all_pages = Page.objects.filter(document__project=project).order_by('document__document_id', 'tk_page_number')
        add_details(f"Parsing {all_pages.count()} pages.", project_id, DETAIL_JOB_NAME)
        for page in all_pages:
            parse_time = timezone.now()

            page_parser = PageFileParser(parser_config=parser_config)
            page_parser.add_file(page.xml_file.path)
            page_parser.parse()
            page.parsed_data = page_parser.get_alto_files()[0].get_standalone_json_object()
            page.last_parsed_at = parse_time
            page.save(current_user=extracting_user)

            processed_steps += 1
            set_progress(processed_steps, total_steps, project_id)
            add_details(f"Parsed page {page.tk_page_id} (p. {page.tk_page_number})", project_id, DETAIL_JOB_NAME)

        set_progress(100, project_id, PROGRESS_JOB_NAME)
        set_details("FINISHED", project_id, DETAIL_JOB_NAME)
    except Project.DoesNotExist:
        set_progress(100, project_id, PROGRESS_JOB_NAME)
        set_details("Project not found", project_id, DETAIL_JOB_NAME)


def stream_extraction_progress(request, project_id):
    """This function streams the progress of the extraction process to the client."""
    set_progress(0, project_id, PROGRESS_JOB_NAME)

    def event_stream():
        while True:
            progress = cache.get(f'{project_id}_{PROGRESS_JOB_NAME}', 0)
            yield f'data: {progress}\n\n'
            if progress >= 100:
                break
            time.sleep(1)  # Sleep for one second before checking again

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def stream_extraction_progress_detail(request, project_id):
    """This function streams the details of the extraction process to the client."""
    add_details("Processing files", project_id, DETAIL_JOB_NAME)

    def event_stream():
        while True:
            details = cache.get(f'{project_id}_{DETAIL_JOB_NAME}', 'no details available')
            if details:
                yield f'data: {details}\n\n'
            if details == "FINISHED":
                yield 'event: complete\ndata: Process completed.\n\n'
                break
            set_details('', project_id, DETAIL_JOB_NAME)    # Clear after sending
            time.sleep(.5)  # Sleep half a second before checking again

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
