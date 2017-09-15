import unittest

from stringsheet.parser import create_spreadsheet_values
from stringsheet.parser import create_language_sheet_values
from stringsheet.parser import parse_resources


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.resources = parse_resources('test-resources/res')


class CreateSpreadsheetValuesTestCase(BaseTestCase):
    def setUp(self):
        super(CreateSpreadsheetValuesTestCase, self).setUp()
        self.values = create_spreadsheet_values(self.resources)

    def test_rows_are_valid(self):
        rows = [
            ['id', 'comment', 'default', 'de', 'pl', 'zh-rCN', 'zh-rTW'],
            ['a_string', '', 'A string', '', '', '', ''],
            ['partly_added', '', 'Partly added', 'Partly added (de)', '', '',
             ''],
            ['string', 'String with comment', 'String', 'String (de)',
             'String (pl)', 'String (zh-rCN)', 'String (zh-rTW)'],
            ['string_2', '', 'String 2', '', '', '', ''],
            ['array[0]', 'Item comment', 'First', '', '', '', ''],
            ['array[1]', '', 'Second', '', '', '', ''],
            ['array_comment[0]', 'Array comment', 'Some item', '', '', '', ''],
            ['array_comment[1]', 'Array comment', 'More items', '', '', '', ''],
            ['array_comment[2]', 'Comment', 'More', '', '', '', ''],
            ['plural{zero}', 'Parent comment', 'Other', '', '', '', ''],
            ['plural{one}', 'Parent comment', 'One', '', '', '', ''],
            ['plural{two}', 'Parent comment', 'Other', '', '', '', ''],
            ['plural{few}', 'Parent comment', 'Other', '', '', '', ''],
            ['plural{many}', 'Parent comment', 'Other', '', '', '', ''],
            ['plural{other}', 'Comment', 'Other', '', '', '', ''],
            ['plurals{zero}', 'Item comment', 'Zero', '', '', '', ''],
            ['plurals{one}', '', 'One', '', '', '', ''],
            ['plurals{two}', '', 'Two', '', '', '', ''],
            ['plurals{few}', '', 'Few', '', '', '', ''],
            ['plurals{many}', '', 'Many', '', '', '', ''],
            ['plurals{other}', '', 'Other', '', '', '', ''],
        ]
        self.assertEqual(len(rows), len(self.values))
        for index, row in enumerate(rows):
            self.assertEqual(row, self.values[index])


class CreateLanguageSpreadsheetValuesTestCase(BaseTestCase):
    def setUp(self):
        super(CreateLanguageSpreadsheetValuesTestCase, self).setUp()
        self.values = create_language_sheet_values(self.resources, 'de')

    def test_rows_are_valid(self):
        rows = [
            ['id', 'comment', 'default', 'de'],
            ['a_string', '', 'A string', ''],
            ['partly_added', '', 'Partly added', 'Partly added (de)'],
            ['string', 'String with comment', 'String', 'String (de)'],
            ['string_2', '', 'String 2', ''],
            ['array[0]', 'Item comment', 'First', ''],
            ['array[1]', '', 'Second', ''],
            ['array_comment[0]', 'Array comment', 'Some item', ''],
            ['array_comment[1]', 'Array comment', 'More items', ''],
            ['array_comment[2]', 'Comment', 'More', ''],
            ['plural{zero}', 'Parent comment', 'Other', ''],
            ['plural{one}', 'Parent comment', 'One', ''],
            ['plural{two}', 'Parent comment', 'Other', ''],
            ['plural{few}', 'Parent comment', 'Other', ''],
            ['plural{many}', 'Parent comment', 'Other', ''],
            ['plural{other}', 'Comment', 'Other', ''],
            ['plurals{zero}', 'Item comment', 'Zero', ''],
            ['plurals{one}', '', 'One', ''],
            ['plurals{two}', '', 'Two', ''],
            ['plurals{few}', '', 'Few', ''],
            ['plurals{many}', '', 'Many', ''],
            ['plurals{other}', '', 'Other', ''],
        ]
        self.assertEqual(len(rows), len(self.values))
        for index, row in enumerate(rows):
            self.assertEqual(row, self.values[index])


class CreateTemplateSpreadsheetValuesTestCase(BaseTestCase):
    def setUp(self):
        super(CreateTemplateSpreadsheetValuesTestCase, self).setUp()
        self.values = create_language_sheet_values(self.resources, 'Template')

    def test_rows_are_valid(self):
        rows = [
            ['id', 'comment', 'default', 'language-id'],
            ['a_string', '', 'A string', ''],
            ['partly_added', '', 'Partly added', ''],
            ['string', 'String with comment', 'String', ''],
            ['string_2', '', 'String 2', ''],
            ['array[0]', 'Item comment', 'First', ''],
            ['array[1]', '', 'Second', ''],
            ['array_comment[0]', 'Array comment', 'Some item', ''],
            ['array_comment[1]', 'Array comment', 'More items', ''],
            ['array_comment[2]', 'Comment', 'More', ''],
            ['plural{zero}', 'Parent comment', 'Other', ''],
            ['plural{one}', 'Parent comment', 'One', ''],
            ['plural{two}', 'Parent comment', 'Other', ''],
            ['plural{few}', 'Parent comment', 'Other', ''],
            ['plural{many}', 'Parent comment', 'Other', ''],
            ['plural{other}', 'Comment', 'Other', ''],
            ['plurals{zero}', 'Item comment', 'Zero', ''],
            ['plurals{one}', '', 'One', ''],
            ['plurals{two}', '', 'Two', ''],
            ['plurals{few}', '', 'Few', ''],
            ['plurals{many}', '', 'Many', ''],
            ['plurals{other}', '', 'Other', ''],
        ]
        self.assertEqual(len(rows), len(self.values))
        for index, row in enumerate(rows):
            self.assertEqual(row, self.values[index])


if __name__ == '__main__':
    unittest.main()
