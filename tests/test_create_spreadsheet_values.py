import unittest

from stringsheet.parser import create_spreadsheet_values
from stringsheet.parser import parse_resources


class CreateSpreadsheetValuesTestCase(unittest.TestCase):
    def setUp(self):
        strings = parse_resources('test-resources/res')
        self.values = create_spreadsheet_values(strings)

    def test_contains_all_strings_and_title_row(self):
        self.assertEqual(len(self.values), 11)

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

    def test_order_is_valid(self):
        self.assertEqual('partly_added', self.values[1][0])
        self.assertEqual('string', self.values[2][0])
        self.assertEqual('array[0]', self.values[3][0])
        self.assertEqual('array[1]', self.values[4][0])
        self.assertEqual('plurals{zero}', self.values[5][0])
        self.assertEqual('plurals{one}', self.values[6][0])
        self.assertEqual('plurals{two}', self.values[7][0])
        self.assertEqual('plurals{few}', self.values[8][0])
        self.assertEqual('plurals{many}', self.values[9][0])
        self.assertEqual('plurals{other}', self.values[10][0])

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

    def test_arrays_are_valid(self):
        array_0 = self.values[3]
        self.assertEqual(array_0[0], 'array[0]')
        self.assertEqual(array_0[1], '')
        self.assertEqual(array_0[2], 'First')
        self.assertEqual(array_0[3], '')
        self.assertEqual(array_0[4], '')
        self.assertEqual(array_0[5], '')
        self.assertEqual(array_0[6], '')

        array_1 = self.values[4]
        self.assertEqual(array_1[0], 'array[1]')
        self.assertEqual(array_1[1], '')
        self.assertEqual(array_1[2], 'Second')
        self.assertEqual(array_1[3], '')
        self.assertEqual(array_1[4], '')
        self.assertEqual(array_1[5], '')
        self.assertEqual(array_1[6], '')


if __name__ == '__main__':
    unittest.main()
