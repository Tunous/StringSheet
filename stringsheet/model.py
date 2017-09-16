from operator import attrgetter

from stringsheet import comparator


def _is_translatable(element):
    return element.get('translatable', 'true').lower() == 'true'


def _is_reference(element):
    return element.text.startswith(('@', '?'))


class String:
    """Model representing <string> tag in Android string resources."""

    def __init__(self, name, text, comment):
        self.text = text
        self.name = name
        self.comment = comment

    @staticmethod
    def is_valid(element):
        return (element.tag == 'string' and
                'name' in element.attrib and
                _is_translatable(element) and
                not _is_reference(element))


class StringArrayItem:
    """Model representing <item> tag for arrays in Android string resources."""

    def __init__(self, text, comment):
        self.text = text
        self.comment = comment

    @staticmethod
    def is_valid(element):
        return element.tag == 'item' and not _is_reference(element)


class StringArray:
    """Model representing <string-array> tag in Android string resources."""

    def __init__(self, name, comment):
        self.name = name
        self.comment = comment
        self._items = []

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def insert(self, index, item):
        self._items.insert(index, item)

    def add_item(self, text, comment):
        item = StringArrayItem(text, comment)
        self._items.append(item)

    @staticmethod
    def is_valid(element):
        return (element.tag == 'string-array' and
                'name' in element.attrib and
                _is_translatable(element))


class PluralItem:
    """Model representing <plurals> tag in Android string resources."""

    def __init__(self, quantity, text, comment):
        self.quantity = quantity
        self.text = text
        self.comment = comment

    @staticmethod
    def is_valid(element):
        return (element.tag == 'item' and
                'quantity' in element.attrib and
                not _is_reference(element))


class PluralString:
    """Model representing <item> tag for plurals in Android string resources."""

    def __init__(self, name, comment):
        self.name = name
        self.comment = comment
        self._items = {}

    def __getitem__(self, quantity):
        return self._items[quantity]

    def __setitem__(self, quantity, plural_item):
        self._items[quantity] = plural_item

    def __len__(self):
        return len(self._items)

    def __contains__(self, quantity):
        return quantity in self._items

    @property
    def sorted_items(self):
        return sorted(self._items.values(),
                      key=lambda item: comparator.quantity_order(item.quantity))

    @staticmethod
    def is_valid(element):
        return (element.tag == 'plurals' and
                'name' in element.attrib and
                _is_translatable(element))


class Resources:
    """Model representing <resources> tag in Android string resources."""

    def __init__(self):
        self._strings = {}
        self._arrays = {}
        self._plurals = {}

    def __contains__(self, item):
        return (item in self._strings
                or item in self._arrays
                or item in self._plurals)

    @staticmethod
    def is_valid(element):
        return element.tag == 'resources' and _is_translatable(element)

    @property
    def sorted_strings(self):
        """Return a sorted list of strings stored in this model.

        Returns:
            list: List of strings sorted alphabetically based on their name.
        """
        return sorted(self._strings.values(), key=attrgetter('name'))

    @property
    def sorted_arrays(self):
        """Return a sorted list of arrays stored in this model.

        Returns:
            list: List of string arrays sorted alphabetically based on their
                name.
        """
        return sorted(self._arrays.values(), key=attrgetter('name'))

    @property
    def sorted_plurals(self):
        """Return a sorted list of plurals stored in this model

        Returns:
            list: List of plurals stored alphabetically based on their name.
        """
        return sorted(self._plurals.values(), key=attrgetter('name'))

    def count(self):
        """Return a number of all models stored in this model.

        Returns:
            int: Number of strings, string arrays and plurals.
        """
        return len(self._strings) + len(self._arrays) + len(self._plurals)

    def item_count(self):
        """Return a number of all translatable items stored in this model.

        The translatable items are these XML tags:
         - string
         - string-array > item
         - plurals > item

        This value corresponds to the number of rows that should be created
        in a spreadsheet to store all strings.

        Returns:
            int: Number of all translatable items.
        """
        array_item_count = sum([len(it) for it in self._arrays.values()])
        plural_item_count = sum([len(it) for it in self._plurals.values()])
        return len(self._strings) + array_item_count + plural_item_count

    def get_string_text(self, name):
        """Return text of a string with the specified name."""
        return self._strings[name].text if name in self._strings else ''

    def get_array_text(self, name, index):
        if name not in self._arrays:
            return ''
        return self._arrays[name].sorted_items[index].text

    def get_plural_text(self, name, quantity):
        if name not in self._plurals:
            return ''
        plural = self._plurals[name]
        return plural[quantity].text if quantity in plural else ''

    def add_string(self, string):
        self._strings[string.name] = string

    def add_array(self, string_array):
        self._arrays[string_array.name] = string_array

    def add_plural(self, plural):
        self._plurals[plural.name] = plural

    def add_array_item(self, name, text, comment, index):
        if name not in self._arrays:
            self._arrays[name] = StringArray(name, '')
        self._arrays[name].insert(index, StringArrayItem(text, comment))

    def add_plural_item(self, name, text, comment, quantity):
        if name not in self._plurals:
            self._plurals[name] = PluralString(name, '')
        self._plurals[name][quantity] = PluralItem(quantity, text, comment)


class ResourceContainer:
    """Model containing string resources for multiple languages.

    This model works like a dictionary and stores resources for languages
    mapped by their id.
    """

    def __init__(self):
        self._resources_by_language = {}

    def __getitem__(self, language):
        return self._resources_by_language[language]

    def __setitem__(self, language, resources):
        self._resources_by_language[language] = resources

    def __contains__(self, language):
        return language in self._resources_by_language

    def __len__(self):
        return len(self._resources_by_language)

    def update(self, language, resources):
        if language not in self._resources_by_language:
            self._resources_by_language[language] = resources
        else:
            existing = self._resources_by_language[language]
            for string in resources.sorted_strings:
                existing.add_string(string)
            for array in resources.sorted_arrays:
                existing.add_array(array)
            for plural in resources.sorted_plurals:
                existing.add_plural(plural)

    def languages(self):
        """Return a sorted list of languages stored in this model.

        Returns:
            list: List of language ids sorted alphabetically.
        """
        keys = self._resources_by_language.keys()
        return sorted([it for it in keys if it != 'default'])
