"""
Test archivist fixtures
"""

from copy import deepcopy

from unittest import TestCase

from archivist.archivist import Archivist


# pylint: disable=missing-docstring


FIXTURE1 = {
    "assets": {
        "attributes": {
            "arc_display_type": "door",
            "arc_namespace": "testfixtures",
            "size": "large",
            "data": [
                "data0",
                "data1",
            ],
        },
    },
}
FIXTURE2 = {
    "assets": {
        "attributes": {
            "arc_display_type": "card",
            "arc_namespace": "testfixtures",
            "colour": "blue",
            "data": [
                "data0",
                "data2",
                "data3",
            ],
        },
    },
}
FIXTURE3 = {
    "assets": {
        "attributes": {
            "arc_display_type": "card",
            "arc_namespace": "testfixtures",
            "colour": "blue",
            "size": "large",
            "data": [
                "data0",
                "data2",
                "data3",
            ],
        },
    },
}


class TestFixtures(TestCase):
    """
    Test Archivist class fixtures
    """

    maxDiff = None

    def test_fixtures(self):
        """
        Test default archivist creation
        """
        arch = Archivist("url", auth="authauthauth")
        self.assertEqual(
            arch.fixtures,
            {},
            msg="Incorrect fixtures",
        )
        arch.fixtures = FIXTURE1
        self.assertEqual(
            arch.fixtures,
            FIXTURE1,
            msg="Incorrect fixtures",
        )

        # prove that deepcopy recreates all underlying fixtures
        newarch = deepcopy(arch)

        newarch.fixtures = FIXTURE2
        self.assertEqual(
            newarch.fixtures,
            FIXTURE3,
            msg="Incorrect fixtures",
        )

        # but original arch is untouched
        self.assertEqual(
            arch.fixtures,
            FIXTURE1,
            msg="Incorrect fixtures",
        )
