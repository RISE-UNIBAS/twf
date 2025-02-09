"""This module contains Celery tasks for loading metadata from Google Sheets."""
import json

from celery import shared_task

from twf.clients.google_sheets_client import GoogleSheetsClient
from twf.models import Project, Document, User, Page
from twf.tasks.task_base import start_task, fail_task, update_task, end_task, get_project_and_user


@shared_task(bind=True)
def load_json_metadata(self, project_id, user_id, data_file, data_target_type, json_data_key, match_to_field):
    """This function loads metadata from a JSON file."""

    try:
        project, user = get_project_and_user(project_id, user_id)
    except ValueError as e:
        raise ValueError(str(e)) from e

    task, percentage_complete = start_task(self, project, user_id, "Load Metadata from JSON File",
                                           text="Starting to load metadata from Json File...")

    # Open uploaded file and read the content as json
    data = data_file.read()
    data = json.loads(data)

    # Iterate over the data and save the metadata
    for item in data:
        id_value_of_item = item[json_data_key]

        if data_target_type == 'document':
            try:
                document = None
                if match_to_field == 'dbid':
                    document = Document.objects.get(project=project, id=id_value_of_item)
                elif match_to_field == 'docid':
                    document = Document.objects.get(project=project, document_id=id_value_of_item)
                    print("Found document", document)
                if document:
                    document.metadata['import'] = item
                    document.save(current_user=self.request.user)
                    print("Saved document", document)

            except Document.DoesNotExist:
                print(f"Document with {match_to_field} {id_value_of_item} does not exist.")

        elif data_target_type == 'page':
            try:
                page = None
                if match_to_field == 'dbid':
                    page = Page.objects.get(document__project=project, id=id_value_of_item)
                elif match_to_field == 'docid':
                    page = Page.objects.get(document__project=project, dbid=id_value_of_item)
                if page:
                    page.metadata['import'] = item
                    page.save(current_user=self.request.user)
            except Page.DoesNotExist:
                print(f"Page with {match_to_field} {id_value_of_item} does not exist.")


    end_task(self, task, "Finished loading metadata from JSON File.")


@shared_task(bind=True)
def load_sheets_metadata(self, project_id, user_id):
    """This function loads metadata from Google Sheets.
    :param self: Celery task
    :param project_id: Project ID
    :param user_id: User ID"""

    try:
        project, user = get_project_and_user(project_id, user_id)
    except ValueError as e:
        raise ValueError(str(e)) from e


    task, percentage_complete = start_task(self, project, user_id, "Load Metadata from Google Sheets",
                                           text="Starting to load metadata from Google Sheets...")

    sheets_configuration = project.get_task_configuration('google_sheet')
    auth_json = 'transkribusWorkflow/google_key.json'
    table_data = GoogleSheetsClient.get_data_from_spreadsheet(auth_json,
                                                              sheets_configuration["sheet_id"],
                                                              sheets_configuration["range"])
    title_row = table_data[0]
    table_data = table_data[1:]
    processed_table_lines = 0
    total_table_lines = len(table_data)
    doc_id_column_index = title_row.index(sheets_configuration["document_id_column"])

    valid_cols = []
    valid_cols_str = sheets_configuration["valid_columns"]
    if valid_cols_str:
        valid_cols = valid_cols_str.split(',')

    for table_line in table_data:
        special_cols = [sheets_configuration["document_title_column"],]
        cols_to_check = valid_cols + special_cols
        doc_id = int(table_line[doc_id_column_index])
        try:
            doc = Document.objects.get(document_id=doc_id)
            doc.metadata['google_sheets'] = {}
            for column in cols_to_check:
                try:
                    index = title_row.index(column)
                    value = table_line[index]
                    if column == sheets_configuration["document_title_column"]:
                        doc.title = value
                    else:
                        doc.metadata['google_sheets'][column] = value
                    # print(f'Column {column} found in metadata for document {doc_id}.')
                except IndexError:
                    value = ''
                    print(f'Column {column} not found in metadata for document {doc_id}. IE')
                except ValueError:
                    value = ''
                    print(f'Column {column} not found in metadata for document {doc_id}. VE')

            doc.save(current_user=user)
            update_task(self, task, "", processed_table_lines, total_table_lines)

        except Document.DoesNotExist:
            doc = None
            print(f'Document with ID {doc_id} not found.')

        processed_table_lines += 1

    end_task(self, task, "Finished loading metadata from Google Sheets.")
