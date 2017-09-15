import unittest

from stringsheet.parser import parse_directory


class ParseDirectoryTestCase(unittest.TestCase):
    """Test that the parser can find strings in all XML files under the
    specified directory.
    """

    def setUp(self):
        self.resources = parse_directory('test-resources/strings')

    def test_finds_all_strings(self):
        self.assertEqual(2, self.resources.count(),
                         'Found incorrect number of strings')


class ParseNonExistingDirectoryTestCase(unittest.TestCase):
    """Test that the parser handles non-existing files."""

    def test_crashes(self):
        with self.assertRaises(OSError):
            parse_directory('test-resources/non_existing')


class ParseDirectoryWithNonTranslatableFileTestCase(unittest.TestCase):
    """Test that the parser doesn't parse strings from "donottranslate.xml"
    files.
    """

    def setUp(self):
        self.resources = parse_directory(
            'test-resources/strings_non_translatable_file')

    def test_doesnt_find_string_in_non_translatable_file(self):
        self.assertNotIn('non_translatable', self.resources)


if __name__ == '__main__':
    unittest.main()
