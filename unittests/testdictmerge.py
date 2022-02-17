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
        self.assertEqual(
            dictmerge._deepmerge(
                {"key": "value", "sub": {"subkey": "subvalue"}},
                {"key1": "value1", "sub1": {"subkey1": "subvalue1"}},
            ),
            {
                "key": "value",
                "sub": {"subkey": "subvalue"},
                "key1": "value1",
                "sub1": {"subkey1": "subvalue1"},
            },
            msg="Dictmerge returns incorrect result",
        )

    def test_dotdict(self):
        """
        Test dotdict
        """
        self.assertIsNone(
            dictmerge._dotdict(None),
            msg="Dotdict returns incorrect result",
        )
        self.assertEqual(
            dictmerge._dotdict({}),
            {},
            msg="Dotdict returns incorrect result",
        )
        self.assertEqual(
            dictmerge._dotdict({"key1": "value1"}),
            {"key1": "value1"},
            msg="Dotdict returns incorrect result",
        )
        self.assertEqual(
            dictmerge._dotdict({"key": "value", "sub": {"subkey": "subvalue"}}),
            {"key": "value", "sub.subkey": "subvalue"},
            msg="Dotdict returns incorrect result",
        )
