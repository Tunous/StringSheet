import unittest

from stringsheet.parser import parse_resources


class ResourcesParseTestCase(unittest.TestCase):
    """Test that parser correctly extracts strings from Android resources
    directory
    """

    def setUp(self):
        self.resources = parse_resources('test-resources/res')
        self.languages = ['pl', 'de', 'zh-rCN', 'zh-rTW']

    def test_finds_all_languages(self):
        self.assertIn('default', self.resources)
        for language in self.languages:
            self.assertIn(language, self.resources)

    def test_number_of_languages_is_correct(self):
        self.assertEqual(len(self.resources), 5)

    def test_doesnt_find_invalid_languages(self):
        self.assertNotIn('night', self.resources)
        self.assertNotIn('v21', self.resources)
        self.assertNotIn('w820dp', self.resources)

    def test_finds_all_strings(self):
        self.assertIn('string', self.resources['default'])
        for language in self.languages:
            self.assertIn('string', self.resources[language])

    def test_translations_are_correct(self):
        self.assertEqual('String',
                         self.resources['default']._strings['string'].text)
        for language in self.languages:
            self.assertEqual('String (' + language + ')',
                             self.resources[language]._strings['string'].text)

    def test_non_existing_translations_are_skipped(self):
        self.assertIn('partly_added', self.resources['default'])
        self.assertIn('partly_added', self.resources['de'])
        self.assertNotIn('partly_added', self.resources['pl'])


if __name__ == '__main__':
    unittest.main()
