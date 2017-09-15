import unittest

from stringsheet.main import create_link


class LinkTestCase(unittest.TestCase):
    def test_creates_valid_link(self):
        self.assertEqual(
            'https://docs.google.com/spreadsheets/d/theSpreadsheetId/edit',
            create_link('theSpreadsheetId'))


if __name__ == '__main__':
    unittest.main()
