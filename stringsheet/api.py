import os

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'StringSheet'


def _get_credentials():
    """Get valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(
        credential_dir,
        'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_service():
    """Construct a Resource for interacting with Google Spreadsheets API."""
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
    return discovery.build('sheets', 'v4', http=http,
                           discoveryServiceUrl=discovery_url)


def create_spreadsheet(service, body):
    return service.spreadsheets().create(body=body).execute()


def get_spreadsheet(service, spreadsheet_id):
    return service.spreadsheets().get(
        spreadsheetId=spreadsheet_id
    ).execute()


def batch_update_values(service, spreadsheet_id, body):
    return service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body
    ).execute()


def batch_get_values(service, spreadsheet_id, ranges):
    return service.spreadsheets().values().batchGet(
        spreadsheetId=spreadsheet_id,
        ranges=ranges
    ).execute()


def batch_update(service, spreadsheet_id, requests):
    return service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()


def create_add_sheet_request(sheet_id, title):
    return {
        'addSheet': {
            'properties': {
                'sheetId': sheet_id,
                'title': title
            }
        }
    }


def create_value_range(language, values):
    return {
        'range': language + "!A:Z",
        'values': values
    }


def create_protected_range_request(sheet_id, start_row_index, end_row_index,
                                   start_column_index, end_column_index,
                                   description):
    return {
        'addProtectedRange': {
            'protectedRange': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': start_row_index,
                    'endRowIndex': end_row_index,
                    'startColumnIndex': start_column_index,
                    'endColumnIndex': end_column_index
                },
                'description': description
            }
        }
    }


def create_frozen_properties_request(sheet_id, frozen_row_count,
                                     frozen_column_count):
    return {
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {
                    'frozenRowCount': frozen_row_count,
                    'frozenColumnCount': frozen_column_count
                }
            },
            'fields': 'gridProperties.frozenRowCount,'
                      'gridProperties.frozenColumnCount'
        }
    }
