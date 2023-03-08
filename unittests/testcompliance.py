"""
Test compliance
"""

from logging import getLogger
from os import environ
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    COMPLIANCE_LABEL,
    COMPLIANCE_POLICIES_LABEL,
    COMPLIANCE_SUBPATH,
    ROOT,
)
from archivist.logger import set_logger

from .mock_response import MockResponse

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

IDENTITY = f"{COMPLIANCE_POLICIES_LABEL}/0000-0000-000000000-00000000"
SUBPATH = f"{COMPLIANCE_SUBPATH}/{COMPLIANCE_LABEL}"
ASSET_ID = "assets/0000-0000-000000000-00000000"

POLICY_RESPONSE = {
    "compliance_policy_identity": IDENTITY,
    "compliant": False,
    "reason": "reason",
}
POLICY_RESPONSE2 = {
    "compliance_policy_identity": IDENTITY,
    "compliant": True,
    "reason": "",
}
RESPONSE = {
    "compliance": [
        POLICY_RESPONSE,
        POLICY_RESPONSE2,
    ],
    "compliant": False,
    "compliant_at": "2019-11-27T14:44:19Z",
}

POLICY = {
    "identity": IDENTITY,
    "description": "policy description",
    "display_name": "policy display_name",
    "asset_filter": [
        ["a", "b"],
        ["x", "z"],
    ],
    "event_display_type": "policy event_display_type",
    "time_period_seconds": 10,
}

if "RKVST_LOGLEVEL" in environ and environ["RKVST_LOGLEVEL"]:
    set_logger(environ["RKVST_LOGLEVEL"])

LOGGER = getLogger(__name__)


class TestCompliance(TestCase):
    """
    Test Archivist Compliance
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()

    def test_compliance_str(self):
        """
        Test compliance str
        """
        self.assertEqual(
            str(self.arch.compliance),
            "ComplianceClient(url)",
            msg="Incorrect str",
        )

    def test_compliance_report(self):
        """
        Test compliance
        """
        with mock.patch.object(self.arch.compliance_policies, "read") as mock_read:
            mock_read.return_value = MockResponse(200, **POLICY)
            self.arch.compliance.compliant_at_report(RESPONSE)
            mock_read.assert_called_once_with(IDENTITY)

    def test_compliance(self):
        """
        Test compliance
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_response = MockResponse(
                200,
                **RESPONSE,
            )
            mock_get.return_value = mock_response

            response = self.arch.compliance.compliant_at(
                ASSET_ID,
            )
            self.assertEqual(
                len(response["compliance"]),
                2,
                msg="incorrect number of compliances",
            )
            self.assertEqual(
                response["compliant"],
                False,
                msg="Incorrect compliant",
            )
            self.assertEqual(
                response["compliant_at"],
                "2019-11-27T14:44:19Z",
                msg="Incorrect compliant_at",
            )
            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/{SUBPATH}/{ASSET_ID}",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                            "params": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_compliance_with_report(self):
        """
        Test compliance
        """
        with mock.patch.object(self.arch.session, "get") as mock_get, mock.patch.object(
            self.arch.compliance_policies, "read"
        ) as mock_read:
            mock_read.return_value = MockResponse(200, **POLICY)
            mock_response = MockResponse(
                200,
                **RESPONSE,
            )
            mock_get.return_value = mock_response

            response = self.arch.compliance.compliant_at(
                ASSET_ID,
                report=True,
            )
            self.assertEqual(
                len(response["compliance"]),
                2,
                msg="incorrect number of compliances",
            )
            mock_read.assert_called_once_with(IDENTITY)
