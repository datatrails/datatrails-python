"""
Test runner compliance
"""
from logging import getLogger
from os import environ
from unittest import TestCase, mock

# from archivist.errors import ArchivistBadRequestError
# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable
from archivist.archivist import Archivist
from archivist.compliance import Compliance
from archivist.compliance_policies import CompliancePolicy
from archivist.logger import set_logger

if "RKVST_LOGLEVEL" in environ and environ["RKVST_LOGLEVEL"]:
    set_logger(environ["RKVST_LOGLEVEL"])

LOGGER = getLogger(__name__)

COMPLIANCE_POLICY_NAME = "ev maintenance policy"
COMPLIANCE_POLICIES_CREATE = {
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
}
IDENTITY = "compliance_policies/c25fb9e7-0a88-4236-8720-1008eb4ddd1d"
COMPLIANCE_POLICIES_RESPONSE = {
    "identity": IDENTITY,
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


class TestRunnerCompliance(TestCase):
    """
    Test Archivist Runner
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_compliance_policies_create(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.compliance_policies, "create_from_data"
        ) as mock_compliance_policies_create, mock.patch.object(
            self.arch.compliance_policies, "delete"
        ) as mock_compliance_policies_delete:
            mock_compliance_policies_create.return_value = CompliancePolicy(
                **COMPLIANCE_POLICIES_RESPONSE
            )
            self.arch.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "COMPLIANCE_POLICIES_CREATE",
                                "description": "Testing compliance_policies_create",
                                "print_response": True,
                                "delete": True,
                            },
                            **COMPLIANCE_POLICIES_CREATE,
                        }
                    ],
                }
            )
            self.assertEqual(
                mock_sleep.call_count,
                0,
                msg="time_sleep incorrectly called",
            )
            mock_compliance_policies_create.assert_called_once_with(
                COMPLIANCE_POLICIES_CREATE
            )
            self.assertEqual(
                self.arch.runner.deletions[IDENTITY],
                self.arch.compliance_policies.delete,
                msg="Incorrect compliance_policy delete_method",
            )
            mock_compliance_policies_delete.assert_called_once()

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_compliance_compliant_at(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.compliance, "compliant_at"
        ) as mock_compliance_compliant_at, mock.patch.object(
            self.arch.runner, "identity"
        ) as mock_identity:
            mock_identity.return_value = COMPLIANCE_COMPLIANT_AT_ID
            mock_compliance_compliant_at.return_value = Compliance(
                **COMPLIANCE_RESPONSE
            )
            self.arch.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "COMPLIANCE_COMPLIANT_AT",
                                "description": "Testing compliance_compliant_at",
                                "print_response": True,
                                "asset_label": COMPLIANCE_COMPLIANT_AT_NAME,
                            },
                        }
                    ],
                }
            )
            self.assertEqual(
                mock_sleep.call_count,
                0,
                msg="time_sleep incorrectly called",
            )
            mock_compliance_compliant_at.assert_called_once_with(
                COMPLIANCE_COMPLIANT_AT_ID
            )
            self.assertEqual(
                len(self.arch.runner.entities),
                0,
                msg="Incorrect compliance created",
            )

    @mock.patch("archivist.runner.time_sleep")
    def test_runner_compliance_compliant_at_non_compliant(self, mock_sleep):
        """
        Test runner operation
        """
        with mock.patch.object(
            self.arch.compliance, "compliant_at"
        ) as mock_compliance_compliant_at, mock.patch.object(
            self.arch.runner, "identity"
        ) as mock_identity:
            mock_identity.return_value = COMPLIANCE_COMPLIANT_AT_ID
            mock_compliance_compliant_at.return_value = Compliance(
                **COMPLIANCE_FALSE_RESPONSE
            )
            self.arch.runner(
                {
                    "steps": [
                        {
                            "step": {
                                "action": "COMPLIANCE_COMPLIANT_AT",
                                "description": "Testing compliance_compliant_at",
                                "print_response": True,
                                "asset_label": COMPLIANCE_COMPLIANT_AT_NAME,
                            },
                            "report": True,
                        }
                    ],
                }
            )
            self.assertEqual(
                mock_sleep.call_count,
                0,
                msg="time_sleep incorrectly called",
            )
            mock_compliance_compliant_at.assert_called_once_with(
                COMPLIANCE_COMPLIANT_AT_ID,
                report=True,
            )
            self.assertEqual(
                len(self.arch.runner.entities),
                0,
                msg="Incorrect compliance created",
            )
