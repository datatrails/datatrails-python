"""
Test archivist
"""

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods

from unittest import TestCase

from archivist import dictmerge


class TestDictMerge(TestCase):
    """
    Test dictmerge
    """

    def test_dictmerge(self):
        """
        Test dictmerge
        """
        self.assertEqual(
            dictmerge._deepmerge(None, None),
            {},
            msg="Dictmerge returns incorrect result",
        )
        self.assertEqual(
            dictmerge._deepmerge({"key": "value"}, None),
            {"key": "value"},
            msg="Dictmerge returns incorrect result",
        )
        self.assertEqual(
            dictmerge._deepmerge(None, {"key": "value"}),
            {"key": "value"},
            msg="Dictmerge returns incorrect result",
        )
        self.assertEqual(
            dictmerge._deepmerge(
                {"key": "value"},
                {"key1": "value1"},
            ),
            {"key": "value", "key1": "value1"},
            msg="Dictmerge returns incorrect result",
        )
