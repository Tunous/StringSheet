import os
import sys
import webbrowser

import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'StringSheet'

_BROWSER_OPENED_MESSAGE = """
Your browser has been opened to visit:

    {address}
"""

_CODE_PROMPT = 'Please authenticate and enter verification code: '


def _get_credentials():
    """Get valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.cache', 'credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(
        credential_dir, 'sheets.googleapis.stringsheet.json')

    store = Storage(credential_path)
    credentials = store.get() if os.path.isfile(credential_path) else None

    if not credentials or credentials.invalid:
        flow = client.OAuth2WebServerFlow(
            client_id='544612569534-bul8pt6lt594cilmt545rrte934hanuc'
                      '.apps.googleusercontent.com',
            client_secret='4uo68aoi6j-YjXrCXqKUsyHi',
            scope=SCOPES,
            redirect_uri=client.OOB_CALLBACK_URN,
            auth_uri='https://accounts.google.com/o/oauth2/auth',
            token_uri='https://accounts.google.com/o/oauth2/token'
        )
        flow.user_agent = APPLICATION_NAME
        authorize_url = flow.step1_get_authorize_url()
        webbrowser.open(authorize_url)

        try:
            print(_BROWSER_OPENED_MESSAGE.format(address=authorize_url))
            code = input(_CODE_PROMPT).strip()
        except KeyboardInterrupt:
            sys.exit('\nAuthentication cancelled.')

        try:
            credentials = flow.step2_exchange(code)
        except client.FlowExchangeError as e:
            sys.exit('Authentication has failed: {0}'.format(e))

        print('Storing credentials to ' + credential_path)
        store.put(credentials)
        credentials.set_store(store)

        print('Authentication successful.')

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


def create_protected_range_request(sheet_id, start_row_index):
    return {
        'addProtectedRange': {
            'protectedRange': {
                'range': {
                    'sheetId': sheet_id
                },
                'unprotectedRanges': [{
                    'sheetId': sheet_id,
                    'startRowIndex': start_row_index,
                    'startColumnIndex': 3,
                }],
                'editors': {
                    # Required otherwise protection doesn't work correctly
                    'users': []
                },
                'warningOnly': False
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


def create_conditional_format_request(sheet_id, start_row, end_row,
                                      start_column, end_column):
    return {
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{
                    'sheetId': sheet_id,
                    'startRowIndex': start_row,
                    'endRowIndex': end_row,
                    'startColumnIndex': start_column,
                    'endColumnIndex': end_column
                }],
                'booleanRule': {
                    'condition': {
                        'type': 'BLANK'
                    },
                    'format': {
                        'backgroundColor': {
                            'red': 244 / 255,
                            'green': 199 / 255,
                            'blue': 195 / 255,
                            'alpha': 1
                        }
                    }
                }
            }
        }
    }


def create_spreadsheet_body(title, multi_sheet, languages, row_count):
    if multi_sheet:
        sheets = [{
            'properties': {
                'title': 'Overview',
                'sheetId': 0
            },
        }]

        column_metadata = [{'pixelSize': 250} for _ in range(4)]

        # Add template entry to allow for easy addition of new languages
        # by translators
        languages.insert(0, 'Template')

        sheet_id = 1

        for language in languages:
            sheets.append({
                'properties': {
                    'title': language,
                    'sheetId': sheet_id,
                    'gridProperties': {
                        'rowCount': row_count,
                        'columnCount': 4,
                        'frozenRowCount': 1
                    }
                },
                'data': [{
                    'startColumn': 0,
                    'columnMetadata': column_metadata
                }]
            })
            sheet_id += 1
    else:
        num_columns = len(languages) + 3
        column_metadata = [{'pixelSize': 250} for _ in range(num_columns)]
        sheets = [{
            'properties': {
                'title': 'Translations',
                'sheetId': 0,
                'gridProperties': {
                    'rowCount': row_count,
                    'frozenRowCount': 1,
                    'frozenColumnCount': 3
                }
            },
            'data': [{
                'startColumn': 0,
                'columnMetadata': column_metadata
            }]
        }]
    return {
        'properties': {
            'title': title,
            'defaultFormat': {
                'wrapStrategy': 'WRAP'
            }
        },
        'sheets': sheets
    }
