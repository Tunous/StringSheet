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


def write_strings_file(language, strings):
    """
    :param language:
    :param strings:
    :type strings: dict
    :return:
    """
    root = etree.Element('resources')
    for name, value in strings.items():
        if value:
            etree.SubElement(root, 'string', name=name).text = value

    __indent(root)
    tree = etree.ElementTree(root)
    tree.write('output/values-' + language + '/strings.xml',
               pretty_print=True,
               xml_declaration=True,
               encoding='utf-8',
               with_tail=False)
    pass


def __make_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def write_strings_directory(strings_by_language):
    __make_dir('output')
    for language, strings in strings_by_language.items():
        __make_dir('output/values-' + language)
        write_strings_file(language, strings)
    pass
