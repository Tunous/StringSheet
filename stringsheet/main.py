from . import api
from . import parser
from . import writer


def _add_protected_ranges(result, service, spreadsheet_id):
    num_rows = result['updatedRows']
    num_columns = result['updatedColumns']
    requests = [
        api.create_protected_range_request(0, 0, num_rows, 0, 3, 'Protecting informational columns'),
        api.create_protected_range_request(0, 0, 1, 3, num_columns, 'Protecting language titles')
    ]
    result_protect = api.batch_update(service, spreadsheet_id, requests)
    print(result_protect)


def upload(spreadsheet_id, source_dir='.', project_title=''):
    """Uploads project strings to Google Spreadsheet.

    If ``spreadsheet_id`` is empty a new spreadsheet will be created.

    ``project_title`` is only required when no ``spreadsheet_id`` is specified.
    It will be then used to give a name to the newly created spreadsheet.

    :param spreadsheet_id: The id of the Google spreadsheet to use.
    :type spreadsheet_id: str
    :param source_dir: A path to the directory containing your values
                       directories with strings files. Usually you want to set
                       this to the "res" directory of your Android project.
    :type source_dir: str
    :param project_title: A name of the project.
    :type project_title: str
    """
    service = api.get_service()

    if not spreadsheet_id:
        if not project_title:
            raise ValueError('project_title must be specified when creating new spreadsheet')
        spreadsheet_name = project_title + ' Translation'
        spreadsheet_id = api.create_spreadsheet(service, spreadsheet_name)

    strings = parser.parse_resources(source_dir)
    values = parser.create_spreadsheet_values(strings)

    value_range_body = {'values': values}
    result = api.update_cells(service, spreadsheet_id, 'A:Z', value_range_body)
    print(result)

    _add_protected_ranges(result, service, spreadsheet_id)


def download(spreadsheet_id, target_dir='.'):
    """Parse the spreadsheet with the specified ``spreadsheet_id`` and save
    the result as Android values directories with strings files in the
    specified ``target_dir``.

    If no ``target_dir`` is specifies then values directories will be created
    under current working directory.

    :param spreadsheet_id: The id of the Google spreadsheet to parse.
    :param target_dir: A path to the directory where the resulting files should
                       be saved. Usually you want to set this to the "res"
                       directory of your Android project.
    :raise ValueError: If ``spreadsheet_id`` is not specified.
    """
    if not spreadsheet_id:
        raise ValueError("spreadsheet_id must be specified")

    service = api.get_service()
    result = api.get_cells(service, spreadsheet_id)
    strings_by_language = parser.parse_spreadsheet_result(result)
    writer.write_strings_to_directory(strings_by_language, target_dir)
