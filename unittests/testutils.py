"""
Test utils
"""

# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

from unittest import TestCase

from archivist import utils

SELECTOR = [
    {
        "attributes": [
            "arc_display_name",
            "arc_namespace",
        ],
    },
]
SELECTOR1 = [
    "behaviours",
    {
        "attributes": [
            "arc_display_name",
            "arc_namespace",
        ],
    },
]
SELECTOR2 = [
    "behaviours",
]

DATA = {
    "behaviours": "behaviour",
    "attributes": {
        "arc_display_name": "display_name",
        "arc_namespace": "namespace",
    },
}


class TestSelector(TestCase):
    """
    Test and_list and or_dict
    """

    def test_selector_with_empty_args(self):
        """
        Test selector
        """
        props, attrs = utils.selector_signature([], {})
        self.assertEqual(
            props,
            None,
            msg="empty select list and data should return None props",
        )
        self.assertEqual(
            attrs,
            None,
            msg="empty select list and data should return None attrs",
        )

    def test_selector_with_no_args(self):
        """
        Test selector
        """
        props, attrs = utils.selector_signature(None, None)
        self.assertEqual(
            props,
            None,
            msg="no select list and data should return None props",
        )
        self.assertEqual(
            attrs,
            None,
            msg="no select list and data should return None attrs",
        )

    def test_selector_with_empty_selector(self):
        """
        Test selector
        """
        props, attrs = utils.selector_signature(None, DATA)
        self.assertEqual(
            props,
            None,
            msg="no select list should return None props",
        )
        self.assertEqual(
            attrs,
            None,
            msg="no select list should return None attrs",
        )

    def test_selector(self):
        """
        Test selector
        """
        props, attrs = utils.selector_signature(SELECTOR, DATA)
        self.assertEqual(
            props,
            {},
            msg="select list with no props should return None props",
        )
        self.assertEqual(
            attrs,
            {
                "arc_display_name": "display_name",
                "arc_namespace": "namespace",
            },
            msg="select list with no props should return some attrs",
        )

    def test_selector_with_props(self):
        """
        Test selector
        """
        props, attrs = utils.selector_signature(SELECTOR1, DATA)
        self.assertEqual(
            props,
            {"behaviours": "behaviour"},
            msg="select list with props should return some props",
        )
        self.assertEqual(
            attrs,
            {
                "arc_display_name": "display_name",
                "arc_namespace": "namespace",
            },
            msg="select list with props should return some attrs",
        )

    def test_selector_only_props(self):
        """
        Test selector
        """
        props, attrs = utils.selector_signature(SELECTOR2, DATA)
        self.assertEqual(
            props,
            {"behaviours": "behaviour"},
            msg="select list with props should return some props",
        )
        self.assertEqual(
            attrs,
            None,
            msg="select list with only props should return None attrs",
        )
