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
