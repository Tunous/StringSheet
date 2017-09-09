import os

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'StringSheets'


def __get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_service():
    """Constructs a Resource for interacting with Google Spreadsheets API."""
    credentials = __get_credentials()
    http = credentials.authorize(httplib2.Http())
    discovery_url = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
    return discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url)


def create_spreadsheet(service, title):
    """Creates a new spreadsheet with the specified title.

    Args:
        service: Resource, a resource object with methods for interacting with Google Spreadsheets API.
        title: string, a title for the spreadsheet to create.

    Returns:
        An id of the newly created spreadsheet.
    """
    spreadsheet_body = {
        'properties': {
            'title': title
        }
    }
    result = service.spreadsheets().create(body=spreadsheet_body).execute()
    spreadsheet_id = result.get('spreadsheetId')
    print('Created spreadsheet with id:', spreadsheet_id)
    return spreadsheet_id


def get_cells(service, spreadsheet_id, spreadsheet_range='A:Z'):
    return service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=spreadsheet_range
    ).execute()


def update_cells(service, spreadsheet_id, spreadsheet_range, value_range_body):
    return service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=spreadsheet_range,
        body=value_range_body,
        valueInputOption='RAW'
    ).execute()


def batch_update(service, spreadsheet_id, requests):
    return service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": requests}
    ).execute()


def create_protected_range_request(sheet_id, start_row_index, end_row_index, start_column_index, end_column_index,
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


def create_frozen_properties_request(sheet_id, frozen_row_count, frozen_column_count):
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
