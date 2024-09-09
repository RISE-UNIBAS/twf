import logging
import os
import zipfile

from celery import shared_task
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from simple_alto_parser import PageFileParser

from twf.models import Project, User, Document, Page
from twf.page_file_meta_data_reader import extract_transkribus_file_metadata
from twf.utils.file_utils import delete_all_in_folder


@shared_task(bind=True)
def extract_zip_export_task(self, project_id, user_id):
    percentage_complete = 0
    self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                              'text': 'Starting...'})

    # self.update_state(state='FAILURE', meta={'error': str(e)})
    try:
        # Get the projects to save the documents to
        project = Project.objects.get(pk=project_id)
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
        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': 'Preparing...'})

        # Extract the zip file and search for page.xml files
        with zipfile.ZipFile(zip_file.path, 'r') as zip_ref:
            all_files_info = zip_ref.infolist()
            valid_files = [x for x in all_files_info if "/page/" in x.filename and x.filename.endswith(".xml")]

            total_files = len(valid_files)
            processed_files = 0
            self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                      'text': f'Extracting {total_files} files...'})

            # Save the extracted files to the folder
            unique_id = 1
            copied_files = []
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
                processed_files += 1
                percentage_of_extraction = (processed_files / total_files) * 100
                self.update_state(state='PROGRESS', meta={'current': percentage_complete + percentage_of_extraction/3,
                                                          'total': 100, 'text': f'Extracted {processed_files} files...'})

        percentage_complete = 32
        self.update_state(state='PROGRESS', meta={'current': percentage_complete,
                                                  'total': 100, 'text': f'All files extracted. Processing...'})
        #############################
        # Process the extracted files
        # Document and Page instances are only created if they do not exist yet
        all_existing_documents = list(Document.objects.filter(project=project).values_list('document_id', flat=True))
        created_documents = 0
        processed_documents = 0

        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': f'Processing {total_files} documents...'})

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
                processed_documents += 1
                percentage_of_extraction = (processed_documents / total_files) * 100
                self.update_state(state='PROGRESS', meta={'current': percentage_complete + percentage_of_extraction/3,
                                                          'total': 100, 'text': f'Processed {processed_documents} documents...'})

            else:
                print("ERROR")  # TODO: Handle error

        # Delete all documents that were not in the export
        for doc_id in all_existing_documents:
            Document.objects.filter(project=project, document_id=doc_id).delete()

        percentage_complete = 66
        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': 'All documents processed. Parsing...'})

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
            self.update_state(state='PROGRESS', meta={'current': percentage_complete + percentage_of_parsing/3,
                                                      'total': 100, 'text': f'Parsed {processed_pages} pages...'})

        percentage_complete = 100
        self.update_state(state='PROGRESS', meta={'current': percentage_complete, 'total': 100,
                                                  'text': 'All pages parsed. Done!'})

        return {'status': 'completed'}

    except Project.DoesNotExist:
        error_message = f"Project with id {project_id} does not exist."
        self.update_state(state='FAILURE', meta={'error': error_message})
        raise ValueError(error_message)
    except User.DoesNotExist:
        error_message = f"User with id {user_id} does not exist."
        self.update_state(state='FAILURE', meta={'error': error_message})
        raise ValueError(error_message)