import argparse
import errno
import os

import httplib2
from apiclient import discovery
from lxml import etree
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

from stringsheet.parser import parse_resources
from stringsheet.parser import create_spreadsheet_values

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'StringSheets'


def get_credentials(args):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
        :param args:
        :param args:
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
        credentials = tools.run_flow(flow, store, args)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_service(args):
    """Constructs a Resource for interacting with Google Spreadsheets API."""
    credentials = get_credentials(args)
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
    return service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=spreadsheet_range).execute()


def update_cells(service, spreadsheet_id, spreadsheet_range, value_range_body):
    return service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=spreadsheet_range,
                                                  body=value_range_body, valueInputOption='RAW').execute()


def parse_spreadsheet(service, spreadsheet_id):
    result = get_cells(service, spreadsheet_id)
    cells = result['values']
    count = len(cells)
    title_row = cells[0]
    num_languages = len(title_row) - 3

    strings_by_language = {}

    for i in range(0, num_languages):
        language_index = i + 3
        language = title_row[language_index]
        print('Language:', language)

        language_strings = {}
        for row_num in range(1, count):
            row = cells[row_num]
            string_id = row[0]
            translation = ''
            if len(row) > language_index:
                translation = row[language_index]
            language_strings[string_id] = translation
        strings_by_language[language] = language_strings

    return strings_by_language


def write_strings_file(language, strings):
    """
    :param language:
    :param strings:
    :type strings: dict
    :return:
    """
    root = etree.Element('resources')
    for name, value in strings.items():
        if value:
            etree.SubElement(root, 'string', name=name).text = value
    tree = etree.ElementTree(root)
    tree.write('output/values-' + language + '/strings.xml', pretty_print=True, xml_declaration=True, encoding='utf-8')
    pass


def make_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def write_strings_directory(strings_by_language):
    make_dir('output')
    for language, strings in strings_by_language.items():
        make_dir('output/values-' + language)
        write_strings_file(language, strings)
    pass


def parse_and_upload_strings(service, project_title, spreadsheet_id=''):
    """Uploads project strings to Google Spreadsheet.

    If spreadsheet_id is empty a new spreadsheet will be created.

    Args:
        service: Resource, a resource object with methods for interacting with
                 Google Spreadsheets API.
        project_title: string, a name of the project.
        spreadsheet_id: string, an id of the spreadsheet to update.
    """
    if not spreadsheet_id:
        spreadsheet_name = project_title + ' Translation'
        spreadsheet_id = create_spreadsheet(service, spreadsheet_name)

    strings = parse_resources('res')
    values = create_spreadsheet_values(strings)

    value_range_body = {'values': values}

    result = update_cells(service, spreadsheet_id, 'A:Z', value_range_body)
    print(result)


def upload(args):
    service = get_service(args)
    parse_and_upload_strings(service, 'SwipeNews', args.spreadsheet_id)


def download(args):
    service = get_service(args)
    strings_by_language = parse_spreadsheet(service, args.spreadsheet_id)
    write_strings_directory(strings_by_language)


def parse_args():
    parser = argparse.ArgumentParser(
        parents=[tools.argparser],
        description='Manage Android translations using Google Spreadsheets')
    parser.add_argument('--spreadsheet_id', help='Id of the spreadsheet for use', default='')

    subparsers = parser.add_subparsers(dest='operation', metavar='<operation>')
    subparsers.required = True

    parser_upload = subparsers.add_parser('upload', help='Upload strings files to spreadsheet')
    parser_upload.set_defaults(func=upload)

    parser_download = subparsers.add_parser('download', help='Download spreadsheet as strings files')
    parser_download.set_defaults(func=download)

    return parser.parse_args()


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
