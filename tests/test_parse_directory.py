import unittest

from stringsheet.parser import parse_directory


class ParseDirectoryTestCase(unittest.TestCase):
    """Tests that the parser can find strings in all XML files under specified directory."""

    def setUp(self):
        self.strings = parse_directory('test-resources/strings')

    def test_finds_all_strings(self):
        self.assertEqual(len(self.strings), 2, 'Found incorrect number of strings')


class ParseNonExistingDirectoryTestCase(unittest.TestCase):
    """Tests that the parser handles non-existing files."""

    def test_crashes(self):
        with self.assertRaises(FileNotFoundError):
            parse_directory('test-resources/non_existing')


class ParseDirectoryWithNonTranslatableFileTestCase(unittest.TestCase):
    """Test that the parser doesn't parse strings from "donottranslate.xml" files."""

    def setUp(self):
        self.strings = parse_directory('test-resources/strings_non_translatable_file')

    def test_doesnt_find_string_in_non_translatable_file(self):
        self.assertNotIn('non_translatable', self.strings)


if __name__ == '__main__':
    unittest.main()
