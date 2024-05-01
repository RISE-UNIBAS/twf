"""Manages metadata from Google Sheets."""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class MetadataManager:
    """Manages metadata from Google Sheets."""

    service = None

    @staticmethod
    def initialize_service(service_account_json):
        """Initializes the Google Sheets service object."""
        if MetadataManager.service is None:
            credentials = Credentials.from_service_account_file(
                                                service_account_json,
                                                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])

            MetadataManager.service = build('sheets', 'v4', credentials=credentials)

    @staticmethod
    def get_service(service_account_json):
        """Returns a Google Sheets service object."""
        MetadataManager.initialize_service(service_account_json)
        return MetadataManager.service

    @staticmethod
    def get_title_row(service_account_json, spreadsheet_id, range_name):
        """Returns the title row of a Google Sheet as a list."""
        values = MetadataManager.get_data_from_spreadsheet(service_account_json, spreadsheet_id, range_name)
        if values is not None:
            values = values[0]
        return values

    @staticmethod
    def get_data_from_spreadsheet(service_account_json, spreadsheet_id, range_name):
        """Requests data from a Google Sheet and returns it as a list of lists."""
        sheet = MetadataManager.get_service(service_account_json).spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])

        if not values:
            return None
        return values
