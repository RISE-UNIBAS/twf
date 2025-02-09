"""Celery tasks for exporting data from the project."""
import json
import csv
import pandas as pd
from celery import shared_task
from twf.models import Project
from twf.tasks.task_base import get_project_and_user


@shared_task(bind=True)
def export_documents_task(self, project_id, user_id):
    try:
        project, user = get_project_and_user( project_id, user_id)
    except ValueError as e:
        raise ValueError(str(e)) from e


@shared_task(bind=True)
def export_collections_task(self, project_id, user_id):
    try:
        project, user = get_project_and_user(project_id, user_id)
    except ValueError as e:
        raise ValueError(str(e)) from e



@shared_task(bind=True)
def export_project_task(self, project_id, user_id):
    try:
        project, user = get_project_and_user(project_id, user_id)
    except ValueError as e:
        raise ValueError(str(e)) from e



def export_data_task(self, project_id, export_type, export_format, schema):
    """Export data from a project.
    :param self: Celery task
    :param project_id: Project ID
    :param export_type: Type of data to export (documents or collections)
    :param export_format: Format of the export (json, csv, excel)
    :param schema: Optional schema for filtering the data
    :return: Exported data in the specified format"""

    try:
        # Fetch the project
        project = Project.objects.get(id=project_id)
        data = []

        # Retrieve documents or collections based on export_type
        if export_type == 'documents':
            data = project.documents.all()
        elif export_type == 'collections':
            data = project.collections.all()

        # Apply schema if provided (optional filtering)
        if schema:
            schema_fields = json.loads(schema)
            data = filter_data_by_schema(data, schema_fields)

        # Export based on format
        if export_format == 'json':
            return generate_json(data)
        elif export_format == 'csv':
            return generate_csv(data)
        elif export_format == 'excel':
            return generate_excel(data)

    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise


def filter_data_by_schema(data, schema_fields):
    """Filter data based on the provided schema fields (attributes) of the model.
    :param data: Data to filter
    :param schema_fields: Fields to include in the filtered data
    :return: Filtered data"""
    # This function filters the data based on the provided schema
    filtered_data = []
    for item in data:
        filtered_item = {field: getattr(item, field, '') for field in schema_fields}
        filtered_data.append(filtered_item)
    return filtered_data


def generate_json(data):
    """Convert data to JSON string
    :param data: Data to export
    :return: JSON string"""
    return json.dumps([item.to_dict() for item in data], indent=4)


def generate_csv(data):
    """Convert data to CSV string
    :param data: Data to export
    :return: CSV string"""
    output = []
    fieldnames = data[0].keys() if data else []

    csv_output = csv.DictWriter(output, fieldnames=fieldnames)
    csv_output.writeheader()
    for row in data:
        csv_output.writerow(row)

    return ''.join(output)


def generate_excel(data):
    """Convert data to Excel file
    :param data: Data to export
    :return: Excel file"""
    df = pd.DataFrame(data)
    output = df.to_excel(index=False)
    return output
