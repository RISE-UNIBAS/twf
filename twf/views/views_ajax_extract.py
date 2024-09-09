"""This module contains the functions for extracting page.xml files from a Transkribus export zip file. The extracted
files are then processed and saved to the database."""
import logging
import os
import zipfile
from celery import shared_task

from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from simple_alto_parser import PageFileParser

from twf.models import Project, Document, Page, PageTag, User
from twf.page_file_meta_data_reader import extract_transkribus_file_metadata
from twf.utils.file_utils import delete_all_in_folder
from twf.views.views_ajax_base import set_progress, set_details, calculate_and_set_progress, add_details, \
    base_event_stream, base_detail_event_stream
from twf.tasks.structure_tasks import extract_zip_export_task

PROGRESS_JOB_NAME = "extract-progress"
DETAIL_JOB_NAME = "extract-progress-detail"


def start_extraction(request):
    """Start the extraction process as a Celery task."""
    project_id = request.session.get('project_id')
    user_id = request.user.id

    # Trigger the task
    task = extract_zip_export_task.delay(project_id, user_id)

    # Return the task ID so that the frontend can monitor the task
    return JsonResponse({'status': 'success', 'task_id': task.id})


"""async def start_extraction(request):
    
    get_project_id_async = sync_to_async(get_project_id, thread_sensitive=True)
    project_id = await get_project_id_async(request)

    set_progress(0, project_id, PROGRESS_JOB_NAME)
    extract_zip_export_async = sync_to_async(extract_zip_export, thread_sensitive=True)
    await extract_zip_export_async(project_id, request.user)
    create_page_tags_async = sync_to_async(create_page_tags, thread_sensitive=True)
    await create_page_tags_async(project_id, request.user)
    return JsonResponse({'status': 'success'}, status=200)"""


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
        # Document and Page instances are only created if they do not exist yet
        all_existing_documents = list(Document.objects.filter(project=project).values_list('document_id', flat=True))
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
                processed_steps += 1
                calculate_and_set_progress(processed_steps, total_steps, project_id, PROGRESS_JOB_NAME)
                add_details(f"Processed Page {page_instance.tk_page_id}", project_id, DETAIL_JOB_NAME)

            else:
                print("ERROR")  # TODO: Handle error

        # Delete all documents that were not in the export
        for doc_id in all_existing_documents:
            Document.objects.filter(project=project, document_id=doc_id).delete()

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
        add_details(f"Parsing {all_pages.count()} pages.", project_id, DETAIL_JOB_NAME)
        for page in all_pages:
            parse_time = timezone.now()

            page_parser = PageFileParser(parser_config=parser_config)
            page_parser.add_file(page.xml_file.path)
            page_parser.parse()
            page.parsed_data = page_parser.get_alto_files()[0].get_standalone_json_object()
            page.last_parsed_at = parse_time
            page.save(current_user=extracting_user)

            # Update Processing state
            processed_steps += 1
            set_progress(processed_steps, total_steps, project_id)
            add_details(f"Parsed page {page.tk_page_id} (p. {page.tk_page_number})", project_id, DETAIL_JOB_NAME)

        set_progress(100, project_id, PROGRESS_JOB_NAME)
        set_details("FINISHED", project_id, DETAIL_JOB_NAME)
    except Project.DoesNotExist:
        set_progress(100, project_id, PROGRESS_JOB_NAME)
        set_details("Project not found", project_id, DETAIL_JOB_NAME)


def create_page_tags(project_id, extracting_user):
    """This function extracts tags from the parsed data of the pages."""

    try:
        # Get the projects to save the documents to
        project = Project.objects.get(pk=project_id)
        pages = Page.objects.filter(document__project=project).order_by('document__document_id', 'tk_page_number')

        total_pages = len(pages)
        processed_pages = 0
        assigned_tags = 0
        total_tags = 0

        for page in pages:
            PageTag.objects.filter(page=page).delete()
            parsed_data = page.parsed_data

            # Extract tags from parsed data and save them
            num_tags = 0
            for element in parsed_data["elements"]:
                num_tags += len(element["element_data"]["custom_list_structure"])
                for tag in element["element_data"]["custom_list_structure"]:
                    if not "text" in tag:
                        print("NO TEXT?", tag)  # TODO
                    else:
                        text = tag["text"].strip()
                        del tag["text"]
                        tag = PageTag(page=page, variation=text, variation_type=tag["type"],
                                      additional_information=tag)
                        is_assigned = tag.assign_tag(extracting_user)
                        if is_assigned:
                            assigned_tags += 1
                        total_tags += 1
                        tag.save(current_user=extracting_user)

            page.num_tags = num_tags

            page.parsed_data = parsed_data
            page.last_parsed_at = timezone.now()
            if "page_relevance" in parsed_data["file"] and parsed_data["file"]["page_relevance"] == "no":
                page.is_ignored = True
            page.save()

            processed_pages += 1
            calculate_and_set_progress(processed_pages, total_pages, project_id, PROGRESS_JOB_NAME)
            add_details(f"Extracted Tags for page {page.tk_page_id}.", project_id, DETAIL_JOB_NAME)

        set_progress(100, project_id, PROGRESS_JOB_NAME)
        set_details("FINISHED", project_id, DETAIL_JOB_NAME)

    except Project.DoesNotExist:
        set_progress(100, project_id, PROGRESS_JOB_NAME)
        set_details("Project not found", project_id, DETAIL_JOB_NAME)


def stream_extraction_progress(request):
    """This function streams the progress of the extraction process to the client."""
    project_id = request.session.get('project_id')
    set_progress(0, project_id, PROGRESS_JOB_NAME)

    return StreamingHttpResponse(base_event_stream(project_id, PROGRESS_JOB_NAME),
                                 content_type='text/event-stream')


def stream_extraction_progress_detail(request):
    """This function streams the details of the extraction process to the client."""
    project_id = request.session.get('project_id')
    add_details("Processing files", project_id, DETAIL_JOB_NAME)

    return StreamingHttpResponse(base_detail_event_stream(project_id, DETAIL_JOB_NAME),
                                 content_type='text/event-stream')
