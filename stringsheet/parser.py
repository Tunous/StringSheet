import os

from lxml import etree

from . import comparator
from . import constants
from . import model

_COLUMN_LANGUAGE_ID_TEMPLATE = 'language-id'


def parse_file(source, resources):
    """Parse the ``source`` file and extract all found strings to ``resources``.

    Args:
        source: The source object to parse. Can be any of the following:

            - a file name/path
            - a file object
            - a file-like object
            - a URL using the HTTP or FTP protocol

        resources: The resources model for storing the parsed strings.
    """
    tree = etree.parse(source)
    root = tree.getroot()

    if not model.Resources.is_valid(root):
        return

    latest_comment = ''
    for element in root:
        if element.tag is etree.Comment:
            if element.tail.count('\n') <= 1:
                latest_comment = element.text.strip()
            continue

        name = element.get('name', None)
        if not name:
            latest_comment = ''
            continue

        if model.String.is_valid(element):
            resources.add_string(_parse_string(element, name, latest_comment))

        elif model.StringArray.is_valid(element):
            resources.add_array(_parse_array(element, name, latest_comment))

        elif model.PluralString.is_valid(element):
            resources.add_plural(_parse_plural(element, name, latest_comment))

        latest_comment = ''


def _parse_string(element, name, comment):
    return model.String(name, element.text, comment)


def _parse_array(element, name, comment):
    string_array = model.StringArray(name, comment)
    latest_item_comment = comment
    for item in element:
        if item.tag is etree.Comment:
            latest_item_comment = _parse_comment(item, comment)
            continue

        if model.StringArrayItem.is_valid(item):
            string_array.add_item(item.text, latest_item_comment)

        latest_item_comment = comment
    return string_array


def _parse_plural(element, name, comment):
    plural = model.PluralString(name, comment)
    latest_item_comment = comment
    for item in element:
        if item.tag is etree.Comment:
            latest_item_comment = _parse_comment(item, comment)
            continue

        if model.PluralItem.is_valid(item):
            quantity = item.get('quantity')
            plural[quantity] = model.PluralItem(
                quantity, item.text, latest_item_comment)

        latest_item_comment = comment

    for quantity in constants.QUANTITIES:
        if quantity not in plural:
            # TODO: What to do if plural has no 'other' quantity?
            other = plural['other']
            plural[quantity] = model.PluralItem(
                quantity, other.text, comment)

    return plural


def _parse_comment(item, latest_comment):
    return item.text.strip() if item.tail.count('\n') <= 1 else latest_comment


def _is_file_valid(file_name):
    return file_name.endswith('.xml') and file_name != 'donottranslate.xml'


def parse_directory(directory):
    """Parse XML files located under the specified directory as strings dict.

    The directory argument usually should point to one of the 'values-lang'
    directories located under res directory of an Android project.

    Args:
        directory (str): The path to directory with XML files to parse.

    Returns:
        model.Resources: A model with parsed resources.
    """
    files = os.listdir(directory)
    xml_files = [file_name for file_name in files if _is_file_valid(file_name)]

    resources = model.Resources()
    for file_name in xml_files:
        file_path = os.path.join(directory, file_name)
        parse_file(file_path, resources)
    return resources


def is_language_valid(language):
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
    """Parse all string resources located under the specified `directory``.

    This function assumes that the passed ``directory`` corresponds to the "res"
    directory of an Android project containing "values" directories with strings
    for each language.

    Args:
        directory (str): The path to res directory of an Android project
            containing values directories with strings for each language.

    Returns:
        model.ResourceContainer: A dictionary of strings mapped by language and
            then by string id.
    """
    resources = model.ResourceContainer()
    for child_name in os.listdir(directory):
        if not child_name.startswith('values'):
            continue

        if child_name == 'values':
            language = 'default'
        else:
            _, _, language = child_name.partition('-')

        if is_language_valid(language):
            child_path = os.path.join(directory, child_name)
            resources[language] = parse_directory(child_path)
    return resources


def create_language_sheet_values(resources, language):
    title = language if language != 'Template' else _COLUMN_LANGUAGE_ID_TEMPLATE
    return create_spreadsheet_values(resources, [title])


def create_spreadsheet_values(resources, languages=None):
    """Create rows and columns list that can be used to execute API calls.

    Args:
        resources (model.ResourceContainer): A model with strings parsed
            from Android XML strings files.
        languages (list): List of languages for which to create values. If not
            specified values will be created for all parsed languages.

    Returns:
        list: List of spreadsheet rows and columns.
    """
    if not languages:
        languages = resources.languages()
    rows = [['id', 'comment', 'default'] + languages]

    is_template = (len(languages) == 1
                   and languages[0] == _COLUMN_LANGUAGE_ID_TEMPLATE)

    default_strings = resources['default']
    for string in default_strings.sorted_strings:
        row = [string.name, string.comment, string.text]
        if is_template:
            row.append('')
        else:
            for language in languages:
                row.append(resources[language].get_string_text(string.name))
        rows.append(row)

    for array in default_strings.sorted_arrays:
        for index, item in enumerate(array):
            item_name = '{0}[{1}]'.format(array.name, index)
            row = [item_name, item.comment, item.text]
            if is_template:
                row.append('')
            else:
                for language in languages:
                    row.append(resources[language].get_array_text(
                        array.name, index))
            rows.append(row)

    for plural in default_strings.sorted_plurals:
        for item in plural.sorted_items:
            item_name = '{0}{{{1}}}'.format(plural.name, item.quantity)
            row = [item_name, item.comment, item.text]
            if is_template:
                row.append('')
            else:
                for language in languages:
                    row.append(resources[language].get_plural_text(
                        plural.name, item.quantity))
            rows.append(row)

    return rows


def parse_spreadsheet_values(resource_container, values):
    """Parse the result returned by Google Spreadsheets API call.

    Args:
        resource_container (model.ResourceContainer): A model which will hold
            the parsed resources.
        values (dict): The json values data returned by Google Spreadsheets API.
    """
    title_row = values[0]

    for lang_index in range(2, len(title_row)):
        language = title_row[lang_index]

        resources = model.Resources()
        for row in values[1:]:
            column_count = len(row)
            if column_count < 3:
                # Actual strings shouldn't be separated by an empty row.
                break

            translation = row[lang_index] if column_count > lang_index else ''
            string_id = row[0]
            comment = row[1]
            default_text = row[2]

            if not string_id or not default_text:
                # All strings must have id and a default text.
                break

            if ' ' in string_id:
                # String ids can't contain whitespace characters.
                # TODO: Check for more invalid characters
                break

            array_match = comparator.ARRAY_ID_PATTERN.match(string_id)
            if array_match:
                name = array_match.group(1)
                index = int(array_match.group(2))
                resources.add_array_item(name, translation, comment, index)
                continue

            plural_match = comparator.PLURAL_ID_PATTERN.match(string_id)
            if plural_match:
                name = plural_match.group(1)
                quantity = plural_match.group(2)
                resources.add_plural_item(name, translation, comment, quantity)
                continue

            resources.add_string(model.String(string_id, translation, comment))

        resource_container.update(language, resources)

