"""
Test compliance policy
"""

from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    COMPLIANCE_SUBPATH,
    COMPLIANCE_LABEL,
    COMPLIANCE_POLICIES_LABEL,
)

from .mock_response import MockResponse


# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

IDENTITY = f"{COMPLIANCE_POLICIES_LABEL}/0000-0000-000000000-00000000"
SUBPATH = f"{COMPLIANCE_SUBPATH}/{COMPLIANCE_LABEL}"
ASSET_ID = "assets/0000-0000-000000000-00000000"

POLICY_RESPONSE = {"compliance_policy_identity": IDENTITY, "compliant": False}
RESPONSE = {
    "compliance": [
        POLICY_RESPONSE,
    ],
    "compliant": False,
    "compliant_at": "2019-11-27T14:44:19Z",
}


class TestCompliance(TestCase):
    """
    Test Archivist Compliance
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def test_compliance(self):
        """
        Test compliance
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
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
                1,
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
            for compliance in response["compliance"]:
                self.assertEqual(
                    compliance,
                    POLICY_RESPONSE,
                    msg="Incorrect policy response listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/{SUBPATH}/{ASSET_ID}",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                            "params": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )
