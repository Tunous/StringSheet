import unittest

from stringsheet.parser import parse_resources
from stringsheet.parser import create_spreadsheet_values


class CreateSpreadsheetValuesTestCase(unittest.TestCase):
    def setUp(self):
        strings = parse_resources('test-resources/res')
        self.values = create_spreadsheet_values(strings)

    def test_contains_all_strings_and_title_row(self):
        self.assertEqual(len(self.values), 3)

    def test_title_row_is_valid(self):
        title_row = self.values[0]
        self.assertEqual(len(title_row), 7)
        self.assertEqual(title_row[0], 'id')
        self.assertEqual(title_row[1], 'comment')
        self.assertEqual(title_row[2], 'default')
        self.assertEqual(title_row[3], 'de')
        self.assertEqual(title_row[4], 'pl')
        self.assertEqual(title_row[5], 'zh-rCN')
        self.assertEqual(title_row[6], 'zh-rTW')

    def test_strings_are_valid(self):
        partly_added_string = self.values[1]
        self.assertEqual(partly_added_string[0], 'partly_added')
        self.assertEqual(partly_added_string[1], '')
        self.assertEqual(partly_added_string[2], 'Partly added')
        self.assertEqual(partly_added_string[3], 'Partly added (de)')
        self.assertEqual(partly_added_string[4], '')
        self.assertEqual(partly_added_string[5], '')
        self.assertEqual(partly_added_string[6], '')

        string = self.values[2]
        self.assertEqual(string[0], 'string')
        self.assertEqual(string[1], '')
        self.assertEqual(string[2], 'String')
        self.assertEqual(string[3], 'String (de)')
        self.assertEqual(string[4], 'String (pl)')
        self.assertEqual(string[5], 'String (zh-rCN)')
        self.assertEqual(string[6], 'String (zh-rTW)')


if __name__ == '__main__':
    unittest.main()
