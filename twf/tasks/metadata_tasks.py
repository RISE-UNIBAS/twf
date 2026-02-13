"""This module contains Celery tasks for loading metadata from Google Sheets."""

import json
import os

from celery import shared_task

from twf.clients.google_sheets_client import GoogleSheetsClient
from twf.models import Document
from twf.tasks.task_base import BaseTWFTask


def store_metadata(project, doc_id, metadata, user, metadata_storage_key=None):
    """
    Store metadata for a document.

    Args:
        project: The project object
        doc_id: Document ID to match
        metadata: Metadata dict to store
        user: User performing the action
        metadata_storage_key: Optional key under which to nest the metadata.
                              If None or empty, metadata is merged directly.
    """
    try:
        document = project.documents.filter(document_id=doc_id).first()
        if document:
            if metadata_storage_key and metadata_storage_key.strip():
                # Store under the specified key
                document.metadata[metadata_storage_key] = metadata
            else:
                # Merge metadata directly (update existing keys, add new ones)
                if not document.metadata:
                    document.metadata = {}
                document.metadata.update(metadata)
            document.save(current_user=user)
    except Exception as e:
        print(f"Error while storing metadata: {str(e)}")


@shared_task(bind=True, base=BaseTWFTask)
def load_json_metadata(self, project_id, user_id, **kwargs):
    """
    Load metadata from a JSON file.

    Supports two JSON formats:
    1. List of objects: [{"doc_id": "123", "key": "value"}, ...]
       - Use json_data_key to specify which field contains the doc ID
       - Or use match_to_field for alternative matching
    2. Object with IDs as keys: {"123": {"key": "value"}, ...}
       - Keys are used directly as doc IDs
    """
    self.validate_task_parameters(
        kwargs, ["data_file_path", "match_to_field", "data_target_type"]
    )

    data_file_path = kwargs.get("data_file_path")
    metadata_storage_key = kwargs.get("metadata_storage_key", "json_import")
    json_data_key = kwargs.get("json_data_key")
    match_to_field = kwargs.get("match_to_field")

    # Open uploaded file and read the content as json
    try:
        # Read the saved file
        with open(data_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except Exception as e:
        self.end_task(status="FAILURE", error_msg=f"Failed to read JSON file: {str(e)}")
        return

    if isinstance(data, list):
        # Determine which field will be used for matching (same logic as processing)
        id_field = (
            json_data_key
            if json_data_key and json_data_key.strip()
            else match_to_field
        )

        for item in data:
            if not isinstance(item, dict):
                self.end_task(status="FAILURE", error_msg="JSON list contains non-dictionary items")
                return
            if id_field not in item:
                self.end_task(status="FAILURE", error_msg=f"Required field '{id_field}' not found in JSON item")
                return

    elif isinstance(data, dict):
        for key, value in data.items():
            if not isinstance(value, dict):
                self.end_task(status="FAILURE", error_msg="JSON object values must be dictionaries")
                return
    else:
        self.end_task(status="FAILURE", error_msg="JSON data must be either a list or an object")
        return

    # Process metadata
    processed_count = 0
    if isinstance(data, list):
        for item in data:
            # Use json_data_key if provided, otherwise fall back to match_to_field
            id_field = (
                json_data_key
                if json_data_key and json_data_key.strip()
                else match_to_field
            )
            doc_id = item.get(id_field)
            if not doc_id:
                continue  # Skip if no valid document ID
            metadata = item  # Use the full dictionary as metadata
            store_metadata(
                self.project, doc_id, metadata, self.user, metadata_storage_key
            )
            processed_count += 1

    elif isinstance(data, dict):
        for doc_id, metadata in data.items():
            store_metadata(
                self.project, doc_id, metadata, self.user, metadata_storage_key
            )
            processed_count += 1

    # Clean up temporary file
    os.remove(data_file_path)

    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def load_sheets_metadata(self, project_id, user_id, **kwargs):
    """This function loads metadata from Google Sheets.
    :param self: Celery task
    :param project_id: Project ID
    :param user_id: User ID"""

    sheets_configuration = self.project.get_task_configuration("google_sheet")
    auth_json = "transkribusWorkflow/google_key.json"
    table_data = GoogleSheetsClient.get_data_from_spreadsheet(
        auth_json, sheets_configuration["sheet_id"], sheets_configuration["range"]
    )
    title_row = table_data[0]
    table_data = table_data[1:]
    processed_table_lines = 0
    total_table_lines = len(table_data)
    doc_id_column_index = title_row.index(sheets_configuration["document_id_column"])

    valid_cols = []
    valid_cols_str = sheets_configuration["valid_columns"]
    if valid_cols_str:
        valid_cols = valid_cols_str.split(",")

    for table_line in table_data:
        special_cols = [
            sheets_configuration["document_title_column"],
        ]
        cols_to_check = valid_cols + special_cols
        doc_id = int(table_line[doc_id_column_index])
        try:
            doc = Document.objects.get(project=self.project, document_id=doc_id)
            doc.metadata["google_sheets"] = {}
            for column in cols_to_check:
                try:
                    index = title_row.index(column)
                    value = table_line[index]
                    if column == sheets_configuration["document_title_column"]:
                        doc.title = value
                    else:
                        doc.metadata["google_sheets"][column] = value
                    # print(f'Column {column} found in metadata for document {doc_id}.')
                except IndexError:
                    value = ""
                    print(
                        f"Column {column} not found in metadata for document {doc_id}. IE"
                    )
                except ValueError:
                    value = ""
                    print(
                        f"Column {column} not found in metadata for document {doc_id}. VE"
                    )

            doc.save(current_user=self.user)
            self.advance_task()

        except Document.DoesNotExist:
            doc = None
            print(f"Document with ID {doc_id} not found.")

        self.advance_task()

    self.end_task()
