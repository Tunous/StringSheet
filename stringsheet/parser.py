import os

from lxml import etree


def __is_root_valid(root):
    if root.tag != 'resources':
        return False
    return root.get('translatable', 'true').lower() == 'true'


def __is_string_valid(element):
    if element.tag != 'string':
        return False
    if 'name' not in element.attrib:
        return False
    return element.get('translatable', 'true').lower() == 'true'


def parse_file(source):
    """Parse the specified source and extract all the found strings as
     a ``dict`` object.

    Args:
        source: The source object to parse. Can be any of the following:

            - a file name/path
            - a file object
            - a file-like object
            - a URL using the HTTP or FTP protocol

    Returns:
        A ``dict`` object with all the parsed strings mapped as ``id: value``.

        Example:
             ``{'string_id': 'string_value', 'string_id_2', 'string_value_2', ...}``

    """
    tree = etree.parse(source)
    root = tree.getroot()

    if not __is_root_valid(root):
        return {}
    return {
        element.get('name'): element.text
        for element in root
        if __is_string_valid(element)
    }


def __is_file_valid(file):
    return file.endswith('.xml') and file != 'donottranslate.xml'


def parse_directory(directory):
    """Parse all XML files located under the specified ``directory``
    and return found string as a ``dict``.

    :param directory: the path to directory to parse.
    :type directory: str
    :return: A ``dict`` object with all the parsed strings mapped as ``id: value``.
    """
    files = os.listdir(directory)
    xml_files = [file for file in files if __is_file_valid(file)]

    strings = {}
    for file in xml_files:
        file_name = directory + '/' + file
        strings.update(parse_file(file_name))
    return strings


def __is_language_valid(language):
    if language == 'default':
        # Special case for identifying strings in primary language
        return True

    # Language code might contain a country separator
    language, sep, country = language.partition('-r')

    if sep and (not country or len(country) != 2):
        # If there was a separator there also must be a country with a length
        # of 2 letters.
        return False

    # All language codes must be 2 letters long
    return len(language) == 2


def parse_resources(directory):
    """Parse all Android string resources located under the specified
    ``directory``.

    This function assumes that the passed ``directory`` corresponds to the "res"
    directory of an Android project containing "values" directories with strings
    for each language.

    :type directory: str
    :return: dict, dictionary of strings mapped by language and then by string_id.
    """
    strings = {}
    for child_dir in os.listdir(directory):
        if not child_dir.startswith('values'):
            continue

        if child_dir == 'values':
            language = 'default'
        else:
            _, _, language = child_dir.partition('-')

        if not __is_language_valid(language):
            continue

        language_strings = parse_directory(directory + '/' + child_dir)
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


def parse_spreadsheet_result(result):
    cells = result['values']
    count = len(cells)
    title_row = cells[0]

    skip_columns = 2
    num_languages = len(title_row) - skip_columns

    strings_by_language = {}

    for i in range(0, num_languages):
        language_index = i + skip_columns
        language = title_row[language_index]

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
