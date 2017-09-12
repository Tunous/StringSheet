from . import api
from . import parser
from . import writer


def _parse_strings(source_dir):
    print(':: Parsing strings...')
    strings = parser.parse_resources(source_dir)

    num_languages = len(strings)
    num_strings = len(strings['default'])
    print('Found %d languages and %d strings' % (num_languages, num_strings))

    return strings


def _upload(service, spreadsheet_id, strings):
    print(':: Uploading strings...')

    data = []
    requests = []

    free_sheet_id, sheet_id_by_title = _get_sheets(service, spreadsheet_id)
    languages = parser.get_languages(strings)

    num_valid = sum(1 for language in sheet_id_by_title.keys()
                    if parser.is_language_valid(language))
    has_template = 'Template' in sheet_id_by_title

    if num_valid == 0 and not has_template:
        values = parser.create_spreadsheet_values(strings)
        data.append({
            'range': 'A:Z',
            'values': values
        })
    else:
        languages.insert(0, 'Template')
        for language in languages:
            values = parser.create_language_sheet_values(strings, language)
            data.append(api.create_value_range(language, values))

            if language not in sheet_id_by_title:
                requests.append(api.create_add_sheet_request(
                    free_sheet_id, language
                ))
                requests.append(api.create_frozen_properties_request(
                    free_sheet_id, 1, 0
                ))
                free_sheet_id += 1

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
    sheet_id_by_title = {}
    free_sheet_id = 1
    for sheet in response['sheets']:
        properties = sheet['properties']
        sheet_id = properties['sheetId']
        title = properties['title']
        sheet_id_by_title[title] = sheet_id
        free_sheet_id = max(free_sheet_id, sheet_id + 1)
    return free_sheet_id, sheet_id_by_title


def _authenticate():
    print(':: Authenticating...')
    service = api.get_service()
    return service


def _get_sheet_ranges(service, spreadsheet_id):
    spreadsheet = api.get_spreadsheet(service, spreadsheet_id)
    ranges = []

    for sheet in spreadsheet['sheets']:
        title = sheet['properties']['title']
        if parser.is_language_valid(title):
            ranges.append("'%s'" % title)

    return ranges if ranges else ['A:Z']


def _create_spreadsheet(service, project_name, multi_sheet, strings):
    print(':: Creating spreadsheet...')
    spreadsheet_name = project_name + ' (Translations)'
    spreadsheet_body = api.create_spreadsheet_body(
        spreadsheet_name,
        multi_sheet,
        parser.get_languages(strings))
    response = api.create_spreadsheet(service, spreadsheet_body)

    spreadsheet_id = response['spreadsheetId']
    print('Created new spreadsheet with id:', spreadsheet_id)

    return spreadsheet_id


def _write_strings(strings_by_language, target_dir):
    print(':: Saving string files...')
    writer.write_strings_to_directory(strings_by_language, target_dir)

    print('Saved all strings to "%s"' % target_dir)


def _download_strings(service, spreadsheet_id):
    print(':: Downloading strings...')
    ranges = _get_sheet_ranges(service, spreadsheet_id)
    response = api.batch_get_values(service, spreadsheet_id, ranges)

    strings_by_language = {}
    for value_range in response['valueRanges']:
        if 'values' not in value_range:
            continue
        values = value_range['values']
        strings_by_language.update(parser.parse_spreadsheet_values(values))

    num_languages = len(strings_by_language) - 1
    print('Downloaded translations in %d languages:' % num_languages)

    total_strings = len(strings_by_language['default'])

    for language in strings_by_language:
        if language == 'default':
            continue

        language_strings = strings_by_language[language]
        num_strings = sum(1 for string_id in language_strings
                          if language_strings[string_id])
        progress = (num_strings / total_strings) * 100
        print(' > %s: %d/%d (%d%%)'
              % (language, num_strings, total_strings, progress))

    return strings_by_language


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
    service = _authenticate()
    strings = _parse_strings(source_dir)
    spreadsheet_id = _create_spreadsheet(service, project_name, multi_sheet,
                                         strings)
    _upload(service, spreadsheet_id, strings)

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


def upload(spreadsheet_id, source_dir='.'):
    """Uploads project strings to Google Spreadsheet.

    If ``spreadsheet_id`` is empty a new spreadsheet will be created.

    ``project_title`` is only required when no ``spreadsheet_id`` is specified.
    It will be then used to give a name to the newly created spreadsheet.

    Args:
        spreadsheet_id (str): The id of the Google Spreadsheet to use.
        source_dir (str): A path to the resources directory of your Android
            project.
    """
    service = _authenticate()
    strings = _parse_strings(source_dir)
    _upload(service, spreadsheet_id, strings)


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
    service = _authenticate()
    strings_by_language = _download_strings(service, spreadsheet_id)
    _write_strings(strings_by_language, target_dir)
