import errno
import os

from lxml import etree


def __indent(element, indent_char='\t', level=0):
    indent_text = '\n' + level * indent_char
    if len(element):
        if not element.text or not element.text.strip():
            element.text = indent_text + indent_char
        if not element.tail or not element.tail.strip():
            element.tail = indent_text
        for element in element:
            __indent(element, indent_char, level + 1)
        if not element.tail or not element.tail.strip():
            element.tail = indent_text
    elif level and (not element.tail or not element.tail.strip()):
        element.tail = indent_text


def write_strings_file(directory, strings):
    """
    :param directory:
    :param strings:
    :type strings: dict
    :return:
    """
    root = etree.Element('resources')
    for name, value in sorted(strings.items()):
        if value:
            etree.SubElement(root, 'string', name=name).text = value

    __indent(root)
    tree = etree.ElementTree(root)
    tree.write(directory + '/strings.xml',
               pretty_print=True,
               xml_declaration=True,
               encoding='utf-8',
               with_tail=False)


def __make_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def write_strings_to_directory(strings_by_language, target_dir):
    """
    :param strings_by_language:
    :param target_dir:
    :type target_dir: str
    :return:
    """
    __make_dir(target_dir)
    for language, strings in strings_by_language.items():
        if not target_dir.endswith('/'):
            target_dir += '/'
        if language == 'default':
            values_dir = target_dir + 'values'
        else:
            values_dir = target_dir + 'values-' + language
        __make_dir(values_dir)

        write_strings_file(values_dir, strings)
