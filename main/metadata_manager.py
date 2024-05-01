import time

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class MetadataManager:

    service = None

    @staticmethod
    def initialize_service(service_account_json):
        if MetadataManager.service is None:
            credentials = Credentials.from_service_account_file(
                                                service_account_json,
                                                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])

            MetadataManager.service = build('sheets', 'v4', credentials=credentials)

    @staticmethod
    def get_service(service_account_json):
        MetadataManager.initialize_service(service_account_json)
        return MetadataManager.service

    @staticmethod
    def get_title_row(service_account_json, spreadsheet_id, range_name):
        values = MetadataManager.get_data_from_spreadsheet(service_account_json, spreadsheet_id, range_name)
        if values is not None:
            values = values[0]
        return values

    @staticmethod
    def get_data_from_spreadsheet(service_account_json, spreadsheet_id, range_name):
        sheet = MetadataManager.get_service(service_account_json).spreadsheets()
        start_time = time.time()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        end_time = time.time()
        print(f"Time taken to get data: {end_time - start_time} seconds")
        values = result.get('values', [])

        if not values:
            return None
        return values

