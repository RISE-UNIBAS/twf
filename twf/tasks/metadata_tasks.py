"""This module contains Celery tasks for loading metadata from Google Sheets."""
from celery import shared_task

from twf.clients.google_sheets_client import GoogleSheetsClient
from twf.models import Project, Document, User
from twf.tasks.task_base import start_task, fail_task, update_task, end_task


@shared_task(bind=True)
def load_sheets_metadata(self, project_id, user_id):
    """This function loads metadata from Google Sheets.
    :param self: Celery task
    :param project_id: Project ID
    :param user_id: User ID"""

    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist as e:
        self.update_state(state='FAILURE', meta={'error': f'Project with ID {project_id} not found.'})
        raise ValueError(f'Project with ID {project_id} not found.') from e

    task, percentage_complete = start_task(self, project, user_id, "Load Metadata from Google Sheets",
                                           text="Starting to load metadata from Google Sheets...")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist as e:
        fail_task(self, task, f'User with ID {user_id} not found.')
        raise ValueError(f'User with ID {user_id} not found.') from e

    auth_json = 'transkribusWorkflow/google_key.json'
    table_data = GoogleSheetsClient.get_data_from_spreadsheet(auth_json,
                                                              project.metadata_google_sheet_id,
                                                              project.metadata_google_sheet_range)
    title_row = table_data[0]
    table_data = table_data[1:]
    processed_table_lines = 0
    total_table_lines = len(table_data)
    doc_id_column_index = title_row.index(project.metadata_google_doc_id_column)

    for table_line in table_data:
        special_cols = [project.metadata_google_title_column,]
        cols_to_check = project.get_valid_cols() + special_cols
        doc_id = int(table_line[doc_id_column_index])
        try:
            doc = Document.objects.get(document_id=doc_id)
            doc.metadata['google_sheets'] = {}
            for column in cols_to_check:
                try:
                    index = title_row.index(column)
                    value = table_line[index]
                    if column == project.metadata_google_title_column:
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
