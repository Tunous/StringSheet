import json
import unittest

from stringsheet.parser import parse_spreadsheet_values


class BaseSpreadsheetDataTestCase(unittest.TestCase):
    @property
    def test_file(self):
        raise NotImplementedError

    def setUp(self):
        with open('test-resources/output/%s' % self.test_file) as f:
            output = json.load(f)
            values = output['values']
            self.strings_by_language = parse_spreadsheet_values(values)


class ValidDataTestCase(BaseSpreadsheetDataTestCase):
    test_file = 'valid.json'

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


class EmptyRowTestCase(BaseSpreadsheetDataTestCase):
    test_file = 'empty_row.json'

    def test_finds_correct_number_of_strings(self):
        for language in ['default', 'de', 'pl']:
            strings = self.strings_by_language[language]
            self.assertEqual(len(strings), 2)
            self.assertIn('string', strings)
            self.assertIn('string_2', strings)


class RowWithMissingIdTestCase(BaseSpreadsheetDataTestCase):
    test_file = 'missing_id_row.json'

    def test_finds_correct_number_of_strings(self):
        for language in ['default', 'de', 'pl']:
            strings = self.strings_by_language[language]
            self.assertEqual(len(strings), 2)
            self.assertIn('string', strings)
            self.assertIn('string_2', strings)


class RowWithIncorrectlyNamedIdTestCase(BaseSpreadsheetDataTestCase):
    test_file = 'incorrectly_named_id.json'

    def test_finds_correct_number_of_strings(self):
        for language in ['default', 'de', 'pl']:
            strings = self.strings_by_language[language]
            self.assertEqual(len(strings), 2)
            self.assertIn('string', strings)
            self.assertIn('string_2', strings)


if __name__ == '__main__':
    unittest.main()
