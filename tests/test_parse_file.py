import unittest

from stringsheet.parser import parse_file
from stringsheet.writer import get_strings_text
from stringsheet.model import Resources


class BaseParseTestCase(unittest.TestCase):
    @property
    def test_file(self):
        raise NotImplementedError

    @property
    def output_file(self):
        return self.test_file

    def setUp(self):
        self.resources = Resources()
        parse_file(self.test_file, self.resources)
        with open(self.output_file, mode='rb') as file:
            self.raw_text = file.read()

    def assert_string(self, name: str, text: str, comment: str = ''):
        string = self.resources._strings[name]
        self.assertEqual(string.text, text, "String text is invalid")
        self.assertEqual(string.comment, comment, "String comment is invalid")


class ParseBasicStringsTestCase(BaseParseTestCase):
    """Test that the parser can correctly find strings in a XML file."""

    test_file = 'test-resources/strings_basic.xml'

    def test_finds_all_strings(self):
        self.assertEqual(2, self.resources.count(),
                         'Found incorrect number of strings')

    def test_finds_correct_id(self):
        self.assertIn('test_string', self.resources, 'String is missing')
        self.assertIn('second_string', self.resources, 'String is missing')

    def test_strings_have_correct_values(self):
        self.assert_string('test_string', 'Test string')
        self.assert_string('second_string', 'Second string')

    def test_doesnt_contain_unknown_strings(self):
        self.assertNotIn('unknown', self.resources,
                         'Found string not present in file')

    def test_output_is_valid(self):
        self.assertEqual(self.raw_text, get_strings_text(self.resources),
                         'Result file is different from required')


class ParseNotTranslatableStringsTestCase(BaseParseTestCase):
    """Test that the parser doesn't find strings set to not translatable."""

    test_file = 'test-resources/strings_not_translatable.xml'
    output_file = 'test-resources/strings_not_translatable_output.xml'

    def test_finds_all_strings(self):
        self.assertEqual(2, self.resources.count(),
                         'Found incorrect number of strings')

    def test_doesnt_find_non_translatable_string(self):
        self.assertNotIn('not_translatable', self.resources,
                         'Found non translatable string')

    def test_finds_translatable_strings(self):
        self.assertIn('translatable', self.resources)
        self.assertIn('translatable_2', self.resources)

    def test_output_is_valid(self):
        self.assertEqual(self.raw_text, get_strings_text(self.resources),
                         'Result file is different from required')


class ParseEmptyFileTestCase(BaseParseTestCase):
    """Test that the parser does not create any strings for empty XML files."""

    test_file = 'test-resources/strings_empty.xml'

    def test_doesnt_find_any_strings(self):
        self.assertEqual(0, self.resources.count(),
                         'Found strings in empty file')


class ParseNotTranslatableRootTestCase(BaseParseTestCase):
    """Test that the parser does not find strings in XML file with
    non-translatable root.
    """

    test_file = 'test-resources/strings_not_translatable_root.xml'

    def test_doesnt_find_any_strings(self):
        self.assertEqual(0, self.resources.count(),
                         'Found strings in non-translatable file')


class ParseInvalidRootTestCase(BaseParseTestCase):
    """Test that the parser does not find in XML files with invalid root tag."""

    test_file = 'test-resources/strings_invalid_root_tag.xml'

    def test_doesnt_find_any_strings(self):
        self.assertEqual(0, self.resources.count(),
                         'Found strings in XML file with invalid root tag')


class ParseUnknownElementsTestCase(BaseParseTestCase):
    """Test that the parser only finds strings using the <string> XML tag."""

    test_file = 'test-resources/strings_invalid.xml'

    def test_doesnt_find_any_strings(self):
        self.assertEqual(0, self.resources.count(),
                         'Found strings with invalid tags')


class ParseNonExistingFileTestCase(unittest.TestCase):
    """Test that the parser handles non-existing files."""

    def test_crashes(self):
        with self.assertRaises(OSError):
            parse_file('test-resources/strings_non_existing.xml', Resources())


class ParseArraysTestCase(BaseParseTestCase):
    """Test that the parser handles string arrays."""

    test_file = 'test-resources/strings_arrays.xml'

    def test_finds_all_strings(self):
        self.assertEqual(0, len(self.resources._strings))
        self.assertEqual(2, len(self.resources._arrays))
        self.assertEqual(0, len(self.resources._plurals))

    def test_finds_all_items(self):
        self.assertEqual(3, len(self.resources._arrays['string']._items))
        self.assertEqual(3, len(self.resources._arrays['string_2']._items))

    def test_items_have_valid_text(self):
        items = self.resources._arrays['string']._items
        self.assertEqual('First', items[0].text)
        self.assertEqual('Second', items[1].text)
        self.assertEqual('Third', items[2].text)

        items_2 = self.resources._arrays['string_2']._items
        self.assertEqual('First', items_2[0].text)
        self.assertEqual('Second', items_2[1].text)
        self.assertEqual('Third', items_2[2].text)

    def test_output_is_valid(self):
        self.assertEqual(self.raw_text, get_strings_text(self.resources),
                         'Result file is different from required')

    def test_item_count_is_correct(self):
        self.assertEqual(6, self.resources.item_count())


class ParsePluralsTestCase(BaseParseTestCase):
    """Test that the parser handles plural strings."""

    test_file = 'test-resources/strings_plurals.xml'
    output_file = 'test-resources/strings_plurals_output.xml'

    def test_finds_all_strings(self):
        self.assertEqual(0, len(self.resources._strings))
        self.assertEqual(0, len(self.resources._arrays))
        self.assertEqual(2, len(self.resources._plurals))

    def test_finds_all_items(self):
        self.assertEqual(6, len(self.resources._plurals['string']))
        self.assertEqual(6, len(self.resources._plurals['string_2']))

    def test_items_have_valid_text(self):
        plural = self.resources._plurals['string']
        self.assertIn('zero', plural)
        self.assertIn('one', plural)
        self.assertIn('two', plural)
        self.assertIn('few', plural)
        self.assertIn('many', plural)
        self.assertIn('other', plural)

        plural_2 = self.resources._plurals['string_2']
        self.assertIn('zero', plural_2)
        self.assertIn('one', plural_2)
        self.assertIn('two', plural_2)
        self.assertIn('few', plural_2)
        self.assertIn('many', plural_2)
        self.assertIn('other', plural_2)

    def test_plurals_have_valid_text(self):
        plural = self.resources._plurals['string']
        self.assertEqual('Zero', plural['zero'].text)
        self.assertEqual('One', plural['one'].text)
        self.assertEqual('Two', plural['two'].text)
        self.assertEqual('Few', plural['few'].text)
        self.assertEqual('Many', plural['many'].text)
        self.assertEqual('Other', plural['other'].text)

        plural_2 = self.resources._plurals['string']
        self.assertEqual('Zero', plural_2['zero'].text)
        self.assertEqual('One', plural_2['one'].text)
        self.assertEqual('Other', plural_2['other'].text)

    def test_missing_quantities_are_created_from_other(self):
        plural = self.resources._plurals['string_2']
        self.assertEqual('Other', plural['two'].text)
        self.assertEqual('Other', plural['few'].text)
        self.assertEqual('Other', plural['many'].text)

    def test_output_is_valid(self):
        text = get_strings_text(self.resources)
        self.assertEqual(self.raw_text, text,
                         'Result file is different from required')


class ParseOutputTestCase(BaseParseTestCase):
    """Test that the writer saves strings in order."""

    test_file = 'test-resources/strings_order.xml'
    output_file = 'test-resources/strings_order_output.xml'

    def test_order_is_valid(self):
        self.assertEqual(self.raw_text, get_strings_text(self.resources),
                         'Result file is different from required')


class ParseWithCommentsTestCase(BaseParseTestCase):
    """Test that the parser reads comments."""

    test_file = 'test-resources/strings_comments.xml'
    output_file = 'test-resources/strings_comments.xml'

    def test_string_has_comment(self):
        string = self.resources._strings['string']
        self.assertEqual('String comment', string.comment)

    def test_string_has_no_old_comment(self):
        string = self.resources._strings['string_2']
        self.assertEqual('', string.comment)

    def test_string_has_no_comment_after_blank_line(self):
        string = self.resources._strings['string_3']
        self.assertEqual('', string.comment)

    def test_array_items_have_comments(self):
        array = self.resources._arrays['array']
        self.assertEqual('', array.comment)
        self.assertEqual('Array item comment', array[0].comment)
        self.assertEqual('', array[1].comment)
        self.assertEqual('', array[2].comment)

    def test_array_items_inherit_parent_comment(self):
        array = self.resources._arrays['array_2']
        self.assertEqual('Array comment', array.comment)
        self.assertEqual('Array comment', array[0].comment)
        self.assertEqual('Own comment', array[1].comment)
        self.assertEqual('Array comment', array[2].comment)

    def test_plural_items_have_comments(self):
        plural = self.resources._plurals['plural']
        self.assertEqual('', plural.comment)
        self.assertEqual('Comment', plural['one'].comment)
        self.assertEqual('', plural['two'].comment)
        self.assertEqual('', plural['other'].comment)

    def test_plural_items_inherit_parent_comments(self):
        plural = self.resources._plurals['plural_2']
        self.assertEqual('Plural comment', plural.comment)
        self.assertEqual('Comment', plural['one'].comment)
        self.assertEqual('Plural comment', plural['two'].comment)
        self.assertEqual('Plural comment', plural['other'].comment)


if __name__ == '__main__':
    unittest.main()
