"""
Test or_dict
"""

# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

from unittest import TestCase

from archivist import or_dict


class TestAndList(TestCase):
    """
    Test and_list and or_dict
    """

    def test_or_dict(self):
        """
        Test or_dict
        """
        self.assertEqual(
            or_dict.or_dict(["x", "y"]),
            {"or": ["x", "y"]},
            msg="or_dict returns incorrect result",
        )

    def test_and_list(self):
        """
        Test and_list
        """
        self.assertEqual(
            or_dict.and_list(
                [
                    ["a", "b"],
                    ["x", "y"],
                ]
            ),
            [
                {"or": ["a", "b"]},
                {"or": ["x", "y"]},
            ],
            msg="and_list returns incorrect result",
        )
