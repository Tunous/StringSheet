import json
import unittest

from stringsheet.main import parse_sheet


class SpreadSheetParseTestCase(unittest.TestCase):
    def setUp(self):
        with open('test-resources/output.json') as file:
            output = json.load(file)
            self.strings_by_language = parse_sheet(output)

    def test_finds_all_languages(self):
        self.assertEqual(len(self.strings_by_language), 3)

    def test_finds_correct_languages(self):
        self.assertIn('default', self.strings_by_language)
        self.assertIn('de', self.strings_by_language)
        self.assertIn('pl', self.strings_by_language)

    def test_finds_all_strings(self):
        for language in ['default', 'de', 'pl']:
            strings = self.strings_by_language[language]
            self.assertEqual(len(strings), 2)
            self.assertIn('string', strings)
            self.assertIn('partial_string', strings)


if __name__ == '__main__':
    unittest.main()
