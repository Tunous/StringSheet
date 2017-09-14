import unittest

from stringsheet.comparator import compare_strings
from stringsheet.comparator import string_order


class CompareTestCase(unittest.TestCase):
    def assert_before(self, a, b):
        self.assertLess(compare_strings(a, b), 0)

    def assert_after(self, a, b):
        self.assertGreater(compare_strings(a, b), 0)

    def test_orders_strings_alphabetically(self):
        self.assert_before('a_string', 'b_string')
        self.assert_after('b_string', 'a_string')

    def test_orders_arrays_by_index(self):
        self.assert_before('array[0]', 'array[1]')
        self.assert_after('array[1]', 'array[0]')

    def test_orders_plurals_by_quantity(self):
        self.assert_before('plural{zero}', 'plural{one}')
        self.assert_before('plural{one}', 'plural{two}')
        self.assert_before('plural{two}', 'plural{few}')
        self.assert_before('plural{few}', 'plural{many}')
        self.assert_before('plural{many}', 'plural{other}')

        self.assert_after('plural{other}', 'plural{many}')
        self.assert_after('plural{many}', 'plural{few}')
        self.assert_after('plural{few}', 'plural{two}')
        self.assert_after('plural{two}', 'plural{one}')
        self.assert_after('plural{one}', 'plural{zero}')

    def test_orders_by_type(self):
        self.assert_before('string', 'string[0]')
        self.assert_before('string', 'string{one}')
        self.assert_before('string[0]', 'string{other}')
        self.assert_after('string{zero}', 'string')
        self.assert_after('string{two}', 'string[1]')
        self.assert_after('string[2]', 'string')

    def test_order_is_valid(self):
        actual = [
            'b_plural{one}', 'b_string', 'a_plural{other}', 'b_plural{zero}',
            'a_plural{many}', 'b_array[1]', 'a_array[1]', 'b_array[0]',
            'a_string', 'a_array[0]'
        ]
        expected = [
            'a_string', 'b_string', 'a_array[0]', 'a_array[1]', 'b_array[0]',
            'b_array[1]', 'a_plural{many}', 'a_plural{other}', 'b_plural{zero}',
            'b_plural{one}'
        ]
        self.assertEqual(sorted(actual, key=string_order), expected)


if __name__ == '__main__':
    unittest.main()
