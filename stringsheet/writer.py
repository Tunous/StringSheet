import errno
import os

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


def builds_strings_tree(resources):
    root = etree.Element('resources')

    for string in resources.sorted_strings:
        if not string.text:
            continue

        xml_string = etree.SubElement(root, 'string', name=string.name)
        xml_string.text = string.text

    for array in resources.sorted_arrays:
        has_text = False
        for item in array:
            if item.text:
                has_text = True
                break

        if not has_text:
            continue

        string_array = etree.SubElement(root, 'string-array', name=array.name)
        for item in array:
            etree.SubElement(string_array, 'item').text = item.text

    for plural in resources.sorted_plurals:
        has_text = False
        for item in plural.sorted_items:
            if item.text:
                has_text = True
                break

        if not has_text:
            continue

        plurals = etree.SubElement(root, 'plurals', name=plural.name)
        for item in plural.sorted_items:
            xml_item = etree.SubElement(plurals, 'item', quantity=item.quantity)
            xml_item.text = item.text

    _indent(root)
    return etree.ElementTree(root)


def get_strings_text(resources):
    tree = builds_strings_tree(resources)
    return etree.tostring(tree,
                          pretty_print=True,
                          xml_declaration=True,
                          encoding='utf-8',
                          with_tail=False)


def write_strings_file(directory, resources):
    tree = builds_strings_tree(resources)
    file_path = os.path.join(directory, 'strings.xml')
    tree.write(file_path,
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
    for language in strings_by_language.languages():
        values_dir = os.path.join(target_dir, 'values-' + language)
        _make_dir(values_dir)

        write_strings_file(values_dir, strings_by_language[language])
