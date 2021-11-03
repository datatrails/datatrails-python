"""
Test compliance policy type
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=too-few-public-methods

from unittest import TestCase

from archivist.compliance_policy_type import CompliancePolicyType


class TestCompliancePolicyType(TestCase):
    """
    Test compliance policy type
    """

    def test_compliance_policy_type(self):
        """
        Test ompliance policy type
        """
        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_SINCE.value, 1, msg="Incorrect value"
        )
        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_SINCE.name,
            "COMPLIANCE_SINCE",
            msg="Incorrect name",
        )

        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_CURRENT_OUTSTANDING.value,
            2,
            msg="Incorrect value",
        )
        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_CURRENT_OUTSTANDING.name,
            "COMPLIANCE_CURRENT_OUTSTANDING",
            msg="Incorrect name",
        )

        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_PERIOD_OUTSTANDING.value,
            3,
            msg="Incorrect value",
        )
        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_PERIOD_OUTSTANDING.name,
            "COMPLIANCE_PERIOD_OUTSTANDING",
            msg="Incorrect name",
        )

        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_DYNAMIC_TOLERANCE.value,
            4,
            msg="Incorrect value",
        )
        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_DYNAMIC_TOLERANCE.name,
            "COMPLIANCE_DYNAMIC_TOLERANCE",
            msg="Incorrect name",
        )

        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_RICHNESS.value, 5, msg="Incorrect value"
        )
        self.assertEqual(
            CompliancePolicyType.COMPLIANCE_RICHNESS.name,
            "COMPLIANCE_RICHNESS",
            msg="Incorrect name",
        )
