import unittest

from stringsheet.parser import parse_file
from stringsheet.writer import get_strings_text


class BaseParseTestCase(unittest.TestCase):
    @property
    def test_file(self):
        raise NotImplementedError

    @property
    def output_file(self):
        return self.test_file

    def setUp(self):
        self.strings = parse_file(self.test_file)
        with open(self.output_file, mode='rb') as file:
            self.raw_text = file.read()


class ParseBasicStringsTestCase(BaseParseTestCase):
    """Test that the parser can correctly find strings in a XML file."""

    test_file = 'test-resources/strings_basic.xml'

    def test_finds_all_strings(self):
        self.assertEqual(len(self.strings), 2,
                         'Found incorrect number of strings')

    def test_finds_correct_id(self):
        self.assertIn('test_string', self.strings, 'String is missing')
        self.assertIn('second_string', self.strings, 'String is missing')

    def test_strings_have_correct_values(self):
        self.assertEqual(self.strings['test_string'], 'Test string',
                         'String has incorrect value')
        self.assertEqual(self.strings['second_string'], 'Second string',
                         'String has incorrect value')

    def test_doesnt_contain_unknown_strings(self):
        self.assertNotIn('unknown', self.strings,
                         'Found string not present in file')

    def test_output_is_valid(self):
        self.assertEqual(self.raw_text, get_strings_text(self.strings),
                         'Result file is different from original')


class ParseNotTranslatableStringsTestCase(BaseParseTestCase):
    """Test that the parser doesn't find strings set to not translatable."""

    test_file = 'test-resources/strings_not_translatable.xml'
    output_file = 'test-resources/strings_not_translatable_output.xml'

    def test_finds_all_strings(self):
        self.assertEqual(len(self.strings), 2,
                         'Found incorrect number of strings')

    def test_doesnt_find_non_translatable_string(self):
        self.assertNotIn('not_translatable', self.strings,
                         'Found non translatable string')

    def test_finds_translatable_strings(self):
        self.assertIn('translatable', self.strings)
        self.assertIn('translatable_2', self.strings)

    def test_output_is_valid(self):
        self.assertEqual(self.raw_text, get_strings_text(self.strings),
                         'Result file is different from original')


class ParseEmptyFileTestCase(BaseParseTestCase):
    """Test that the parser does not create any strings for empty XML files."""

    test_file = 'test-resources/strings_empty.xml'

    def test_doesnt_find_any_strings(self):
        self.assertEqual(len(self.strings), 0, 'Found strings in empty file')


class ParseNotTranslatableRootTestCase(BaseParseTestCase):
    """Test that the parser does not find strings in XML file with
    non-translatable root.
    """

    test_file = 'test-resources/strings_not_translatable_root.xml'

    def test_doesnt_find_any_strings(self):
        self.assertEqual(len(self.strings), 0,
                         'Found strings in non-translatable file')


class ParseInvalidRootTestCase(BaseParseTestCase):
    """Test that the parser does not find in XML files with invalid root tag."""

    test_file = 'test-resources/strings_invalid_root_tag.xml'

    def test_doesnt_find_any_strings(self):
        self.assertEqual(len(self.strings), 0,
                         'Found strings in XML file with invalid root tag')


class ParseUnknownElementsTestCase(BaseParseTestCase):
    """Test that the parser only finds strings using the <string> XML tag."""

    test_file = 'test-resources/strings_invalid_element_tag.xml'

    def test_doesnt_find_any_strings(self):
        self.assertEqual(len(self.strings), 0,
                         'Found strings with invalid tags')


class ParseNonExistingFileTestCase(unittest.TestCase):
    """Test that the parser handles non-existing files."""

    def test_crashes(self):
        with self.assertRaises(OSError):
            parse_file('test-resources/strings_non_existing.xml')


class ParsePluralsTestCase(BaseParseTestCase):
    """Test that the parser handles plural strings."""

    test_file = 'test-resources/strings_plurals.xml'
    output_file = 'test-resources/strings_plurals_output.xml'

    def test_finds_all_strings(self):
        self.assertEqual(len(self.strings), 12,
                         'Found incorrect number of strings')

    def test_created_plural_mappings(self):
        self.assertIn('string{zero}', self.strings)
        self.assertIn('string{one}', self.strings)
        self.assertIn('string{two}', self.strings)
        self.assertIn('string{few}', self.strings)
        self.assertIn('string{many}', self.strings)
        self.assertIn('string{other}', self.strings)

        self.assertIn('string_2{zero}', self.strings)
        self.assertIn('string_2{one}', self.strings)
        self.assertIn('string_2{two}', self.strings)
        self.assertIn('string_2{few}', self.strings)
        self.assertIn('string_2{many}', self.strings)
        self.assertIn('string_2{other}', self.strings)

    def test_plurals_have_valid_text(self):
        self.assertEqual('Zero', self.strings['string{zero}'])
        self.assertEqual('One', self.strings['string{one}'])
        self.assertEqual('Two', self.strings['string{two}'])
        self.assertEqual('Few', self.strings['string{few}'])
        self.assertEqual('Many', self.strings['string{many}'])
        self.assertEqual('Other', self.strings['string{other}'])

        self.assertEqual('Zero', self.strings['string_2{zero}'])
        self.assertEqual('One', self.strings['string_2{one}'])
        self.assertEqual('Other', self.strings['string{other}'])

    def test_missing_quantities_are_created_from_other(self):
        self.assertEqual('Other', self.strings['string_2{two}'])
        self.assertEqual('Other', self.strings['string_2{few}'])
        self.assertEqual('Other', self.strings['string_2{many}'])

    def test_output_is_valid(self):
        self.assertEqual(self.raw_text, get_strings_text(self.strings),
                         'Result file is different from original')


if __name__ == '__main__':
    unittest.main()
