import os
from lxml import etree


def __is_valid_root(root):
    if root.tag != 'resources':
        return False
    return root.get('translatable', 'true').lower() == 'true'


def __is_valid_string(element):
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

    if not __is_valid_root(root):
        return {}
    return {
        element.get('name'): element.text
        for element in root
        if __is_valid_string(element)
    }


def parse_directory(directory):
    """Parse all XML files located under the specified ``directory``
    and return found string as a ``dict``.

    :param directory: the path to directory to parse.
    :type directory: str
    :return: A ``dict`` object with all the parsed strings mapped as ``id: value``.
    """
    files = os.listdir(directory)
    xml_files = [file for file in files if file.endswith('.xml')]

    strings = {}
    for file in xml_files:
        file_name = directory + '/' + file
        strings.update(parse_file(file_name))
    return strings
