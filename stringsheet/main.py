from . import api
from . import parser
from . import writer


def _create_spreadsheet_body(title, multi_sheet, languages):
    if multi_sheet:
        sheets = [{
            'properties': {
                'title': 'Overview',
                'index': 0,
            },
        }]

        column_metadata = [{'pixelSize': 250} for _ in range(4)]

        for language in languages:
            sheets.append({
                'properties': {
                    'title': language,
                    'gridProperties': {
                        'columnCount': 4,
                        'frozenRowCount': 1
                    }
                },
                'data': [{
                    'startColumn': 0,
                    'columnMetadata': column_metadata
                }]
            })
    else:
        num_columns = len(languages) + 3
        column_metadata = [{'pixelSize': 250} for _ in range(num_columns)]
        sheets = [{
            'properties': {
                'title': 'Translations',
                'index': 0,
                'gridProperties': {
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
            'title': title
        },
        'sheets': sheets
    }


def create(project_name, source_dir='.', multi_sheet=False):
    """Create new Google Spreadsheet for managing translations.

    Args:
        project_name (str): The name of your Android project. This will
            be used to name the spreadsheet.
        source_dir (str): A path to the resources directory of your
            Android project.
        multi_sheet (bool): Upload each language to a separate sheet
            (in the same file)
    """
    print('Authenticating...')
    service = api.get_service()

    print('Parsing strings...')
    spreadsheet_name = project_name + ' (Translations)'
    strings = parser.parse_resources(source_dir)
    num_languages = len(strings)
    num_strings = len(strings['default'])
    print(' > Found %d languages and %d strings' % (num_languages, num_strings))

    print('Creating spreadsheet...')
    spreadsheet_body = _create_spreadsheet_body(
        spreadsheet_name,
        multi_sheet,
        parser.get_languages(strings))
    response = api.create_spreadsheet(service, spreadsheet_body)
    spreadsheet_id = response['spreadsheetId']
    print(' > Created new spreadsheet with id:', spreadsheet_id)

    response = _upload(service, spreadsheet_id, strings, multi_sheet)

    # TODO: Fix
    # num_rows = result['updatedRows']
    # num_columns = result['updatedColumns']
    # requests = [
    #     api.create_protected_range_request(
    #         0, 0, num_rows, 0, 3, 'Protecting informational columns'),
    #     api.create_protected_range_request(
    #         0, 0, 1, 3, num_columns, 'Protecting language titles'),
    #     api.create_frozen_properties_request(0, 1, 3)
    # ]
    # result_protect = api.batch_update(service, spreadsheet_id, requests)
    # print(result_protect)


def _upload(service, spreadsheet_id, strings, multi_sheet):
    print('Uploading strings...')

    data = []
    requests = []

    if multi_sheet:
        free_sheet_id, language_sheets = _get_sheets(service, spreadsheet_id)

        for language in parser.get_languages(strings):
            values = parser.create_language_sheet_values(strings, language)
            data.append(api.create_value_range(language, values))

            if language not in language_sheets:
                requests.append(api.create_add_sheet_request(
                    free_sheet_id, language
                ))
                requests.append(api.create_frozen_properties_request(
                    free_sheet_id, 1, 0
                ))
                free_sheet_id += 1
    else:
        values = parser.create_spreadsheet_values(strings)
        data.append({
            'range': 'A:Z',
            'values': values
        })

    if requests:
        api.batch_update(service, spreadsheet_id, requests)

    body = {
        'valueInputOption': 'RAW',
        'data': data
    }

    response = api.batch_update_values(service, spreadsheet_id, body)

    print('Strings uploaded:')
    print(' > Updated rows: %d' % response['totalUpdatedRows'])
    print(' > Updated columns: %d' % response['totalUpdatedColumns'])
    print(' > Updated cells: %d' % response['totalUpdatedCells'])
    print(' > Updated sheets: %d' % response['totalUpdatedSheets'])

    return response


def _get_sheets(service, spreadsheet_id):
    response = api.get_spreadsheet(service, spreadsheet_id)
    language_sheets = {}
    free_sheet_id = 1
    for sheet in response['sheets']:
        properties = sheet['properties']
        sheet_id = properties['sheetId']
        title = properties['title']
        language_sheets[title] = sheet_id
        free_sheet_id = max(free_sheet_id, sheet_id + 1)
    return free_sheet_id, language_sheets


def upload(spreadsheet_id, source_dir='.', multi_sheet=False):
    """Uploads project strings to Google Spreadsheet.

    If ``spreadsheet_id`` is empty a new spreadsheet will be created.

    ``project_title`` is only required when no ``spreadsheet_id`` is specified.
    It will be then used to give a name to the newly created spreadsheet.

    Args:
        spreadsheet_id (str): The id of the Google Spreadsheet to use.
        source_dir (str): A path to the resources directory of your Android
            project.
        multi_sheet (bool): Upload each language to a separate sheet
            (in the same file)
    """
    service = api.get_service()
    strings = parser.parse_resources(source_dir)
    _upload(service, spreadsheet_id, strings, multi_sheet)


def _get_sheet_ranges(service, spreadsheet_id):
    spreadsheet = api.get_spreadsheet(service, spreadsheet_id)
    ranges = []
    for sheet in spreadsheet['sheets']:
        cell_range = "'%s'" % sheet['properties']['title']
        ranges.append(cell_range)
    return ranges


def download(spreadsheet_id, target_dir='.'):
    """Parse Google spreadsheet and save the result as Android strings.

    Parse the spreadsheet with the specified ``spreadsheet_id`` and save
    the result as Android values directories with strings files in the
    specified ``target_dir``.

    Args:
        spreadsheet_id (str): The id of the Google spreadsheet to parse.
        target_dir (str): A path to the directory where the resulting files
            should be saved. Usually you want to set this to the resources
            directory of your Android project.
    """
    service = api.get_service()

    ranges = _get_sheet_ranges(service, spreadsheet_id)
    response = api.batch_get_values(service, spreadsheet_id, ranges)

    strings_by_language = {}
    for value_range in response['valueRanges']:
        if 'values' not in value_range:
            continue
        values = value_range['values']
        strings_by_language.update(parser.parse_spreadsheet_values(values))

    writer.write_strings_to_directory(strings_by_language, target_dir)
