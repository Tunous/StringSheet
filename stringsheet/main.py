from . import api
from . import model
from . import parser
from . import writer


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
    resources = _parse_resources(source_dir)
    spreadsheet_id = _create_spreadsheet(service, project_name, multi_sheet,
                                         resources)

    spreadsheet_link = create_link(spreadsheet_id)
    print('Link:', spreadsheet_link)

    _upload(service, spreadsheet_id, resources)
    _create_formatting_rules(service, spreadsheet_id, multi_sheet, resources)
    print()
    print('Success')


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
    resources = _parse_resources(source_dir)
    _upload(service, spreadsheet_id, resources)
    print()
    print('Success')


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
    print()
    print('Success')


def create_link(spreadsheet_id):
    return 'https://docs.google.com/spreadsheets/d/{}/edit'.format(
        spreadsheet_id)


def _authenticate():
    print(':: Authenticating...')
    service = api.get_service()
    return service


def _parse_resources(source_dir):
    print(':: Parsing strings...')
    resources = parser.parse_resources(source_dir)

    num_languages = len(resources.languages())
    num_strings = resources['default'].count()
    print('Found %d languages and %d strings' % (num_languages, num_strings))

    return resources


def _create_spreadsheet(service, project_name, multi_sheet, resources):
    print(':: Creating spreadsheet...')
    spreadsheet_name = project_name + ' (Translations)'
    spreadsheet_body = api.create_spreadsheet_body(
        spreadsheet_name,
        multi_sheet,
        resources.languages(),
        resources['default'].item_count() + 1)
    response = api.create_spreadsheet(service, spreadsheet_body)

    spreadsheet_id = response['spreadsheetId']
    print('Created new spreadsheet with id:', spreadsheet_id)

    return spreadsheet_id


def _upload(service, spreadsheet_id, resources):
    print(':: Uploading strings...')

    data = []
    requests = []

    free_sheet_id, sheet_id_by_title = _get_sheets(service, spreadsheet_id)
    languages = resources.languages()

    num_valid = sum(1 for language in sheet_id_by_title.keys()
                    if parser.is_language_valid(language))
    has_template = 'Template' in sheet_id_by_title

    if num_valid == 0 and not has_template:
        values = parser.create_spreadsheet_values(resources)
        data.append({
            'range': 'A:Z',
            'values': values
        })
    else:
        languages.insert(0, 'Template')
        for language in languages:
            values = parser.create_language_sheet_values(resources, language)
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


def _create_formatting_rules(service, spreadsheet_id, multi_sheet, resources):
    print(':: Creating formatting rules...')
    languages = resources.languages()
    num_languages = len(languages)
    num_columns = num_languages + 3
    num_rows = resources['default'].item_count() + 1
    num_sheets = num_languages + 2 if multi_sheet else 1

    start_index = 1 if multi_sheet else 0

    requests = []
    start_row_index = 1 if multi_sheet else 0
    for i in range(start_index, num_sheets):
        requests.append(api.create_protected_range_request(i, start_row_index))
        requests.append(api.create_conditional_format_request(
            i, 1, num_rows, 3, num_columns))

    api.batch_update(service, spreadsheet_id, requests)


def _download_strings(service, spreadsheet_id):
    print(':: Downloading strings...')
    ranges = _get_sheet_ranges(service, spreadsheet_id)
    response = api.batch_get_values(service, spreadsheet_id, ranges)

    resource_container = model.ResourceContainer()
    for value_range in response['valueRanges']:
        if 'values' not in value_range:
            continue
        values = value_range['values']
        parser.parse_spreadsheet_values(resource_container, values)

    num_languages = len(resource_container) - 1
    print('Downloaded translations in %d languages:' % num_languages)

    total_strings = resource_container['default'].count()

    for language in resource_container.languages():
        language_strings = resource_container[language]
        num_strings = language_strings.count()
        progress = (num_strings / total_strings) * 100
        print(' > %s: %d/%d (%d%%)'
              % (language, num_strings, total_strings, progress))

    return resource_container


def _write_strings(strings_by_language, target_dir):
    print(':: Saving string files...')
    writer.write_strings_to_directory(strings_by_language, target_dir)

    print('Saved all strings to "%s"' % target_dir)


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


def _get_sheet_ranges(service, spreadsheet_id):
    spreadsheet = api.get_spreadsheet(service, spreadsheet_id)
    ranges = []

    for sheet in spreadsheet['sheets']:
        title = sheet['properties']['title']
        if parser.is_language_valid(title):
            ranges.append("'%s'" % title)

    return ranges if ranges else ['A:Z']
