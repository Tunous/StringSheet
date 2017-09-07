import unittest

from stringsheet.parser import parse_file


class ParseBasicStringsTestCase(unittest.TestCase):
    """Tests that the parser can correctly find strings in a XML file."""

    def setUp(self):
        self.strings = parse_file('test-resources/strings_basic.xml')

    def test_finds_all_strings(self):
        self.assertEqual(len(self.strings), 2, 'Found incorrect number of strings')

    def test_finds_correct_id(self):
        self.assertIn('test_string', self.strings, 'String is missing')
        self.assertIn('second_string', self.strings, 'String is missing')

    def test_strings_have_correct_values(self):
        self.assertEqual(self.strings['test_string'], 'Test string', 'String has incorrect value')
        self.assertEqual(self.strings['second_string'], 'Second string', 'String has incorrect value')

    def test_doesnt_contain_unknown_strings(self):
        self.assertNotIn('unknown', self.strings, 'Found string not present in file')


class ParseNotTranslatableStringsTestCase(unittest.TestCase):
    """Tests that the parser doesn't find strings set to not translatable."""

    def setUp(self):
        self.strings = parse_file('test-resources/strings_not_translatable.xml')

    def test_finds_all_strings(self):
        self.assertEqual(len(self.strings), 2, 'Found incorrect number of strings')

    def test_doesnt_find_non_translatable_string(self):
        self.assertNotIn('not_translatable', self.strings, 'Found non translatable string')

    def test_finds_translatable_strings(self):
        self.assertIn('translatable', self.strings)
        self.assertIn('translatable_2', self.strings)


class ParseEmptyFileTestCase(unittest.TestCase):
    """Tests that the parser does not create any strings for empty XML files."""

    def setUp(self):
        self.strings = parse_file('test-resources/strings_empty.xml')

    def test_doesnt_find_any_strings(self):
        self.assertEqual(len(self.strings), 0, 'Found strings in empty file')


class ParseNotTranslatableRootTestCase(unittest.TestCase):
    """Tests that the parser does not find strings in XML file with non-translatable root."""

    def setUp(self):
        self.strings = parse_file('test-resources/strings_not_translatable_root.xml')

    def test_doesnt_find_any_strings(self):
        self.assertEqual(len(self.strings), 0, 'Found strings in non-translatable file')


class ParseInvalidRootTestCase(unittest.TestCase):
    """Tests that the parser does not find in XML files with invalid root tag."""

    def setUp(self):
        self.strings = parse_file('test-resources/strings_invalid_root_tag.xml')

    def test_doesnt_find_any_strings(self):
        self.assertEqual(len(self.strings), 0, 'Found strings in XML file with invalid root tag')


class ParseUnknownElementsTestCase(unittest.TestCase):
    """Tests that the parser only finds strings using the <string> XML tag."""

    def setUp(self):
        self.strings = parse_file('test-resources/strings_invalid_element_tag.xml')

    def test_doesnt_find_any_strings(self):
        self.assertEqual(len(self.strings), 0, 'Found strings with invalid tags')


class ParseNonExistingFileTestCase(unittest.TestCase):
    """Tests that the parser handles non-existing files."""

    def test_crashes(self):
        with self.assertRaises(OSError):
            parse_file('test-resources/strings_non_existing.xml')


if __name__ == '__main__':
    unittest.main()
