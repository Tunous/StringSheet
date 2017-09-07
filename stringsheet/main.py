import errno
import os

from lxml import etree

from . import api
from . import parser


def parse_spreadsheet(service, spreadsheet_id):
    result = api.get_cells(service, spreadsheet_id)
    print(result)
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
        spreadsheet_id = api.create_spreadsheet(service, spreadsheet_name)

    strings = parser.parse_resources('res')
    values = parser.create_spreadsheet_values(strings)

    value_range_body = {'values': values}

    result = api.update_cells(service, spreadsheet_id, 'A:Z', value_range_body)
    print(result)


def upload(spreadsheet_id):
    service = api.get_service()
    parse_and_upload_strings(service, 'SwipeNews', spreadsheet_id)


def download(spreadsheet_id):
    service = api.get_service()
    strings_by_language = parse_spreadsheet(service, spreadsheet_id)
    write_strings_directory(strings_by_language)
