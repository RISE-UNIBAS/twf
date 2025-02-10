"""This module contains Celery tasks for loading metadata from Google Sheets."""
import json
import os

from celery import shared_task

from twf.clients.google_sheets_client import GoogleSheetsClient
from twf.models import Project, Document, User, Page
from twf.tasks.task_base import start_task, fail_task, update_task, end_task, get_project_and_user

def store_metadata(project, doc_id, metadata, user):
    try:
        document = project.documents.filter(document_id=doc_id).first()
        if document:
            document.metadata['json_import'] = metadata
            document.save(current_user=user)
    except Exception as e:
        print(f"Error while storing metadata: {str(e)}")


@shared_task(bind=True)
def load_json_metadata(self, project_id, user_id, data_file_path, data_target_type, json_data_key, match_to_field):
    """This function loads metadata from a JSON file."""

    try:
        project, user = get_project_and_user(project_id, user_id)
    except ValueError as e:
        raise ValueError(str(e)) from e

    task, percentage_complete = start_task(self, project, user_id, "Load Metadata from JSON File",
                                           text="Starting to load metadata from Json File...")

    # Open uploaded file and read the content as json
    try:
        # Read the saved file
        with open(data_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        fail_task(self, task, f"Error while reading the file: {str(e)}")

    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                fail_task(self, task, "Invalid format: List elements must be dictionaries.")
                return
            if match_to_field not in item:
                fail_task(self, task, f"Missing required identifier field '{match_to_field}' in list format.")
                return

    elif isinstance(data, dict):
        for key, value in data.items():
            if not isinstance(value, dict):
                fail_task(self, task, "Invalid format: Dictionary values must be dictionaries.")
                return
    else:
        fail_task(self, task, "Invalid JSON structure: Expected a list or a dictionary.")
        return

    # Process metadata
    processed_count = 0
    if isinstance(data, list):
        for item in data:
            doc_id = item.get(match_to_field)
            if not doc_id:
                continue  # Skip if no valid document ID
            metadata = item  # Use the full dictionary as metadata
            store_metadata(project, doc_id, metadata, user)  # Implement this function
            processed_count += 1

    elif isinstance(data, dict):
        for doc_id, metadata in data.items():
            store_metadata(project, doc_id, metadata, user)  # Implement this function
            processed_count += 1

    # Clean up temporary file
    os.remove(data_file_path)

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
