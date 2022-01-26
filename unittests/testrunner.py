"""
Test runner
"""
from logging import getLogger
from os import environ
from unittest import TestCase

# from archivist.errors import ArchivistBadRequestError

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

from archivist.archivist import Archivist
from archivist.assets import Asset
from archivist.logger import set_logger
from archivist.runner import tree

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

LOGGER = getLogger(__name__)

ASSET_ID = "assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
ASSET_NAME = "radiation bag 1"
ASSETS_RESPONSE = {
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
    "behaviours": ["Attachments", "RecordEvidence"],
    "confirmation_status": "CONFIRMED",
    "identity": ASSET_ID,
}

ASSETS_NO_NAME_RESPONSE = {
    "attributes": {
        "radioactive": True,
        "radiation_level": 0,
        "weight": 0,
    },
    "behaviours": ["Attachments", "RecordEvidence"],
    "confirmation_status": "CONFIRMED",
    "identity": ASSET_ID,
}

COMPLIANCE_POLICY_NAME = "ev maintenance policy"
COMPLIANCE_POLICIES_CREATE_ARGS = [
    {
        "display_name": COMPLIANCE_POLICY_NAME,
        "description": "ev maintenance policy",
        "compliance_type": "COMPLIANCE_DYNAMIC_TOLERANCE",
        "asset_filter": [
            {"or": ["attributes.ev_pump=true"]},
        ],
        "event_display_type": "Maintenance Requested",
        "closing_event_display_type": "Maintenance Performed",
        "dynamic_window": 700,
        "dynamic_variability": 1.5,
    },
]
COMPLIANCE_POLICIES_RESPONSE = {
    "identity": "compliance_policies/c25fb9e7-0a88-4236-8720-1008eb4ddd1d",
    "compliance_type": "COMPLIANCE_DYNAMIC_TOLERANCE",
    "description": "ev maintenance policy",
    "display_name": COMPLIANCE_POLICY_NAME,
    "asset_filter": [{"or": ["attributes.ev_pump=true"]}],
    "event_display_type": "Maintenance Requested",
    "closing_event_display_type": "Maintenance Performed",
    "time_period_seconds": "0",
    "dynamic_window": "700",
    "dynamic_variability": 1.5,
    "richness_assertions": [],
}

COMPLIANCE_COMPLIANT_AT_NAME = "radiation bag 1"
COMPLIANCE_COMPLIANT_AT_ID = "assets/dc0dfc17-1d93-4b7a-8636-f740f40f7f52"
COMPLIANCE_COMPLIANT_AT_ARGS = [
    COMPLIANCE_COMPLIANT_AT_ID,
]
COMPLIANCE_RESPONSE = {
    "compliant": True,
    "compliance": [
        {
            "compliance_policy_identity": (
                "compliance_policies/" "2154d72d-54d2-4da0-b304-3223ab3e09df"
            ),
            "compliant": True,
            "reason": "",
        },
        {
            "compliance_policy_identity": (
                "compliance_policies/" "460c3071-2435-4b1e-9c93-87b1edf6e5e1"
            ),
            "compliant": True,
            "reason": "",
        },
    ],
    "next_page_token": "",
    "compliant_at": "2022-01-28T09:01:27Z",
}
COMPLIANCE_POLICY_NON_COMPLIANT = (
    "compliance_policies/2154d72d-54d2-4da0-b304-3223ab3e09df"
)
COMPLIANCE_FALSE_RESPONSE = {
    "compliant": False,
    "compliance": [
        {
            "compliance_policy_identity": COMPLIANCE_POLICY_NON_COMPLIANT,
            "compliant": False,
            "reason": "Test reason is non compliant",
        },
        {
            "compliance_policy_identity": (
                "compliance_policies/460c3071-2435-4b1e-9c93-87b1edf6e5e1"
            ),
            "compliant": True,
            "reason": "",
        },
    ],
    "next_page_token": "",
    "compliant_at": "2022-01-28T09:01:27Z",
}


class TestRunner(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def test_runner_str(self):
        """
        Test runner str
        """
        self.assertEqual(
            str(self.arch.runner),
            "Runner(url)",
            msg="Incorrect str",
        )

    def test_runner_asset_id(self):
        """
        Test runner asset_id
        """
        runner = self.arch.runner
        runner.entities = tree()
        runner.entities["ASSETS_CREATE"][ASSET_NAME] = Asset(**ASSETS_RESPONSE)
        self.assertEqual(
            runner.asset_id(ASSET_NAME),
            ASSET_ID,
            msg="Incorrect ID",
        )
        self.assertIsNone(
            runner.asset_id(ASSET_NAME + "garbage"),
            msg="Incorrect ID",
        )

    def test_runner_set_entities(self):
        """
        Test runner set_entities
        """
        runner = self.arch.runner
        runner.entities = tree()
        runner.set_entities("ASSETS_CREATE", Asset(**ASSETS_RESPONSE))
        self.assertEqual(
            runner.asset_id(ASSET_NAME),
            ASSET_ID,
            msg="Incorrect ID",
        )
        runner.set_entities("BADASSETS_CREATE", Asset(**ASSETS_NO_NAME_RESPONSE))
        self.assertEqual(
            runner.entities["BADASSETS_CREATE"],
            {},
            msg="Illegal Assets should not be present in entitities",
        )
