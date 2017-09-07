import unittest

from parser import __is_language_valid as is_valid


class LanguageValidationTestCase(unittest.TestCase):
    """Tests that language codes are properly validated."""

    def test_default(self):
        self.assertTrue(is_valid('default'))

    def test_valid(self):
        self.assertTrue(is_valid('en'))
        self.assertTrue(is_valid('pl'))
        self.assertTrue(is_valid('de'))

    def test_incorrect_length(self):
        self.assertFalse(is_valid('enn'))
        self.assertFalse(is_valid('unknown'))
        self.assertFalse(is_valid('a'))
        self.assertFalse(is_valid(''))

    def test_with_separator(self):
        self.assertTrue(is_valid('zh-rCN'))
        self.assertTrue(is_valid('zh-rTW'))

        self.assertFalse(is_valid('zh-CN'))
        self.assertFalse(is_valid('zhh-rCN'))
        self.assertFalse(is_valid('-zh'))
        self.assertFalse(is_valid('zh-'))

    def test_case(self):
        self.assertTrue(is_valid('EN'))
        self.assertTrue(is_valid('eN'))
        self.assertTrue(is_valid('ZH-rCN'))


if __name__ == "__main__":
    unittest.main()
