from . import api
from . import parser
from . import writer


def create(project_name, source_dir='.'):
    """Create new Google Spreadsheet for managing translations.

    Args:
        project_name (str): The name of your Android project. This will be used
            to name the spreadsheet.
        source_dir (str): A path to the resources directory of your Android
            project.
    """
    service = api.get_service()

    spreadsheet_name = project_name + ' (Translations)'
    spreadsheet_id = api.create_spreadsheet(service, spreadsheet_name)

    result = upload(spreadsheet_id, source_dir)

    num_rows = result['updatedRows']
    num_columns = result['updatedColumns']
    requests = [
        api.create_protected_range_request(
            0, 0, num_rows, 0, 3, 'Protecting informational columns'),
        api.create_protected_range_request(
            0, 0, 1, 3, num_columns, 'Protecting language titles'),
        api.create_frozen_properties_request(0, 1, 3)
    ]
    result_protect = api.batch_update(service, spreadsheet_id, requests)
    print(result_protect)


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
    service = api.get_service()

    strings = parser.parse_resources(source_dir)
    values = parser.create_spreadsheet_values(strings)

    value_range_body = {'values': values}
    result = api.update_cells(service, spreadsheet_id, 'A:Z', value_range_body)
    print(result)
    return result


def download(spreadsheet_id, target_dir='.'):
    """Parse Google spreadsheet and save the result as Android strings.

    Parse the spreadsheet with the specified ``spreadsheet_id`` and save
    the result as Android values directories with strings files in the
    specified ``target_dir``.

    Args:
        spreadsheet_id (str): The id of the Google spreadsheet to parse.
        target_dir (str): A path to the directory where the resulting files
            should be saved. Usually you want to set this to the res
            directory of your Android project.

    Raises:
        ValueError: Spreadsheet id was not specified.
    """
    if not spreadsheet_id:
        raise ValueError("spreadsheet_id must be specified")

    service = api.get_service()
    result = api.get_cells(service, spreadsheet_id)
    strings_by_language = parser.parse_spreadsheet_result(result)
    writer.write_strings_to_directory(strings_by_language, target_dir)
