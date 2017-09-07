import unittest

from stringsheet.parser import parse_resources
from stringsheet.parser import create_spreadsheet_values


class ResourcesParseTestCase(unittest.TestCase):
    """Tests that parser correctly extracts strings from Android resources directory"""

    def setUp(self):
        self.strings = parse_resources('test-resources/res')
        self.languages = ['pl', 'de', 'zh-rCN', 'zh-rTW']

    def test_finds_all_languages(self):
        self.assertIn('default', self.strings)
        for language in self.languages:
            self.assertIn(language, self.strings)

    def test_number_of_languages_is_correct(self):
        self.assertEqual(len(self.strings), 5)

    def test_doesnt_find_invalid_languages(self):
        self.assertNotIn('night', self.strings)
        self.assertNotIn('v21', self.strings)
        self.assertNotIn('w820dp', self.strings)

    def test_finds_all_strings(self):
        self.assertIn('string', self.strings['default'])
        for language in self.languages:
            self.assertIn('string', self.strings[language])

    def test_translations_are_correct(self):
        self.assertEqual(self.strings['default']['string'], 'String')
        for language in self.languages:
            self.assertEqual(self.strings[language]['string'], 'String (' + language + ')')

    def test_non_existing_translations_are_skipped(self):
        self.assertIn('partly_added', self.strings['default'])
        self.assertIn('partly_added', self.strings['de'])
        self.assertNotIn('partly_added', self.strings['pl'])


if __name__ == '__main__':
    unittest.main()
