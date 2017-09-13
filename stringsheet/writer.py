import errno
import os
import re

from lxml import etree


def _indent(element, indent_char='\t', level=0):
    indent_text = '\n' + level * indent_char
    if len(element):
        if not element.text or not element.text.strip():
            element.text = indent_text + indent_char
        if not element.tail or not element.tail.strip():
            element.tail = indent_text
        for element in element:
            _indent(element, indent_char, level + 1)
        if not element.tail or not element.tail.strip():
            element.tail = indent_text
    elif level and (not element.tail or not element.tail.strip()):
        element.tail = indent_text


def builds_strings_tree(strings):
    root = etree.Element('resources')
    array_pattern = re.compile('^(\w+)\[(\d+)\]')
    plural_pattern = re.compile('(\w+){(zero|one|two|few|many|other)\}')
    plurals = {}
    arrays = {}
    for name, value in sorted(strings.items()):
        if not value:
            continue

        match = array_pattern.match(name)
        if match:
            array_name = match.group(1)
            index = int(match.group(2))
            array = arrays.get(array_name, [])
            array.insert(index, value)
            arrays[array_name] = array
            continue

        match = plural_pattern.match(name)
        if match:
            plural_name = match.group(1)
            quantity = match.group(2)
            plural = plurals.get(plural_name, {})
            plural[quantity] = value
            plurals[plural_name] = plural
            continue

        etree.SubElement(root, 'string', name=name).text = value

    # Build string arrays
    for name, item_array in sorted(arrays.items()):
        string_array = etree.SubElement(root, 'string-array', name=name)
        for value in item_array:
            etree.SubElement(string_array, 'item').text = value

    # Build plurals
    for name, items in sorted(plurals.items()):
        plural = etree.SubElement(root, 'plurals', name=name)
        for quantity, value in sorted(items.items()):
            etree.SubElement(plural, 'item', quantity=quantity).text = value

    _indent(root)
    return etree.ElementTree(root)


def get_strings_text(strings):
    tree = builds_strings_tree(strings)
    return etree.tostring(tree,
                          pretty_print=True,
                          xml_declaration=True,
                          encoding='utf-8',
                          with_tail=False)


def write_strings_file(directory, strings):
    tree = builds_strings_tree(strings)
    tree.write(directory + '/strings.xml',
               pretty_print=True,
               xml_declaration=True,
               encoding='utf-8',
               with_tail=False)


def _make_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def write_strings_to_directory(strings_by_language, target_dir):
    _make_dir(target_dir)
    for language, strings in strings_by_language.items():
        if not target_dir.endswith('/'):
            target_dir += '/'
        if language == 'default':
            # Do not write strings for the default language. These are supposed
            # to be written manually by developers and they also might contain
            # comments which are not saved when using this script.
            continue
        values_dir = target_dir + 'values-' + language
        _make_dir(values_dir)

        write_strings_file(values_dir, strings)
