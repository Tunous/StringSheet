import argparse
import errno
import os

import httplib2
from apiclient import discovery
from lxml import etree
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'StringSheets'

parser = argparse.ArgumentParser(
    parents=[tools.argparser],
    description='Parse and upload android strings to Google Spreadsheets for translations.')
parser.add_argument('--spreadsheet_id', help='Id of the spreadsheet for use.', default='')
args = parser.parse_args()


def get_credentials():
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
        credentials = tools.run_flow(flow, store, args)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_service():
    """Constructs a Resource for interacting with Google Spreadsheets API."""
    credentials = get_credentials()
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


def parse_spreadsheet():
    service = get_service()
    spreadsheet_id = '1iPsU45FBHMIxnlxqqcu6-qDbmarFbM91lD74xFMeOqo'
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


def get_strings_from_file(file):
    tree = etree.parse(file)
    root = tree.getroot()

    if root.get('translatable', 'true').lower() == 'false':
        print('Found not translatable file: "' + file + '". Skipping...')
        return {}

    strings = {}
    for element in root:
        if element.tag == 'string':
            if element.get('translatable', 'true').lower() == 'false':
                print('Found not translatable string:', element.get('name'))
            else:
                strings[element.get('name')] = element.text

    print('Found', len(strings), 'strings in file: "' + file + '"')
    return strings


def parse_directory(directory):
    files = os.listdir('res/' + directory)
    xml_files = [file for file in files if file.endswith('.xml')]

    all_strings = {}

    for file in xml_files:
        file_name = 'res/' + directory + '/' + file
        strings = get_strings_from_file(file_name)
        all_strings.update(strings)

    return all_strings


def parse_resources():
    """Finds and parses all strings files located under resources directory.

    Returns:
        dict, dictionary of strings mapped by language and then by string_id.
    """
    strings = {}
    for directory in os.listdir('res'):
        if not directory.startswith('values'):
            continue

        if directory == 'values':
            strings["default"] = parse_directory(directory)
            continue

        name_split = directory.split('-', 1)
        if len(name_split) == 2:
            language = name_split[1]
            if language.find('-') >= 0 or len(language) == 2:
                language_strings = parse_directory(directory)
                if language_strings:
                    strings[language] = language_strings

    return strings


def create_spreadsheet_values(strings):
    """Creates strings array that can be used to execute API calls."""
    languages = sorted([it for it in strings.keys() if it != 'default'])
    column_names = ['id', 'comment', 'default'] + languages
    result = [column_names]

    default_strings = strings['default']
    for string_id in sorted(default_strings):
        column = [string_id, '', default_strings[string_id]]
        for language in languages:
            language_strings = strings[language]
            if string_id in language_strings:
                column.append(language_strings[string_id])
            else:
                column.append('')
        result.append(column)

    return result


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

    strings = parse_resources()
    values = create_spreadsheet_values(strings)

    value_range_body = {'values': values}

    result = update_cells(service, spreadsheet_id, 'A:Z', value_range_body)
    print(result)


def main():
    service = get_service()
    parse_and_upload_strings(service, 'SwipeNews', args.spreadsheet_id)


if __name__ == '__main__':
    main()
