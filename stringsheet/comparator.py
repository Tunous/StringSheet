import functools
import re

from . import constants

ARRAY_ID_PATTERN = re.compile('^(\w+)\[(\d+)\]$')
"""Pattern for matching strings in array format.

Example: ``name[0]``
"""

PLURAL_ID_PATTERN = re.compile('^(\w+){(zero|one|two|few|many|other)\}$')
"""Pattern for matching strings in plural format.

Example: ``name{zero}``, ``name{many}``
"""


def _compare_alphabetically(a, b):
    return (a > b) - (a < b)


def _compare_quantities(a, b):
    return constants.QUANTITIES.index(a) - constants.QUANTITIES.index(b)


def compare_strings(a, b):
    """Compare two spreadsheet string ids and return their order.

    The format of provided parameters should be as follows:
     - string_name - regular string
     - string_name[index] - array string
     - string_name{quantity} - plural string

    The order returned by this function is as follows:
     1. Regular strings sorted alphabetically,
     2. String arrays sorted alphabetically, with each array sorted by index.
     3. Plurals sorted alphabetically, with each plural sorted based on
        quantity.

    And the quantity order is as follows: zero, one, two, few, many, other

    Args:
        a (str): The first string in spreadsheet string id format.
        b (str): The second string in spreadsheet string id format.

    Returns:
        int: Positive value if the first id should come before second id,
            negative value if it should come after second id and 0 if both
            ids are equal.
    """
    a_is_array = ARRAY_ID_PATTERN.match(a)
    b_is_array = ARRAY_ID_PATTERN.match(b)
    a_is_plural = PLURAL_ID_PATTERN.match(a)
    b_is_plural = PLURAL_ID_PATTERN.match(b)

    if a_is_array:
        if b_is_plural:
            # Arrays before plurals
            return -1
        if not b_is_array:
            # Arrays after strings
            return 1
        a_name = a_is_array.group(1)
        b_name = b_is_array.group(1)
        if a_name == b_name:
            # For the same array compare by index
            return int(a_is_array.group(2)) - int(b_is_array.group(2))
        return _compare_alphabetically(a_name, b_name)

    if a_is_plural:
        if not b_is_plural:
            # Plurals after strings and arrays
            return 1
        a_name = a_is_plural.group(1)
        b_name = b_is_plural.group(1)
        if a_name == b_name:
            return _compare_quantities(a_is_plural.group(2),
                                       b_is_plural.group(2))
        return _compare_alphabetically(a_name, b_name)

    if b_is_array or b_is_plural:
        # Strings before arrays and plurals
        return -1

    return _compare_alphabetically(a, b)


def quantity_order(quantity):
    return constants.QUANTITIES.index(quantity)


string_order = functools.cmp_to_key(compare_strings)
