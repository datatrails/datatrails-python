"""
Test compliance policy request
"""

# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

from unittest import TestCase

from archivist import compliance_policy_requests


class TestCompliancePolicyRequests(TestCase):
    """
    Test CompliancePolicyRequest
    """

    def test_compliance_policy_since(self):
        """
        Test CompliancePolicySince
        """
        self.assertEqual(
            compliance_policy_requests.CompliancePolicySince(
                description="since description",
                display_name="since display_name",
                asset_filter=[
                    ["a", "b"],
                    ["x", "z"],
                ],
                event_display_type="since event_display_type",
                time_period_seconds=10,
            ).dict(),
            {
                "compliance_type": "COMPLIANCE_SINCE",
                "description": "since description",
                "display_name": "since display_name",
                "asset_filter": [
                    {"or": ["a", "b"]},
                    {"or": ["x", "z"]},
                ],
                "event_display_type": "since event_display_type",
                "time_period_seconds": 10,
            },
            msg="Incorrect dictionary",
        )

    def test_compliance_policy_current_outstanding(self):
        """
        Test CompliancePolicyCurrentOutstanding
        """
        self.assertEqual(
            compliance_policy_requests.CompliancePolicyCurrentOutstanding(
                description="current_outstanding description",
                display_name="current_outstanding display_name",
                asset_filter=[
                    ["a", "b"],
                    ["x", "z"],
                ],
                event_display_type="current_outstanding event_display_type",
                closing_event_display_type="current_outstanding closing_event_display_type",
            ).dict(),
            {
                "compliance_type": "COMPLIANCE_CURRENT_OUTSTANDING",
                "description": "current_outstanding description",
                "display_name": "current_outstanding display_name",
                "asset_filter": [
                    {"or": ["a", "b"]},
                    {"or": ["x", "z"]},
                ],
                "event_display_type": "current_outstanding event_display_type",
                "closing_event_display_type": "current_outstanding closing_event_display_type",
            },
            msg="Incorrect dictionary",
        )

    def test_compliance_policy_period_outstanding(self):
        """
        Test CompliancePolicyequestPeriodOutstanding
        """
        self.assertEqual(
            compliance_policy_requests.CompliancePolicyPeriodOutstanding(
                description="period_outstanding description",
                display_name="period_outstanding display_name",
                asset_filter=[
                    ["a", "b"],
                    ["x", "z"],
                ],
                event_display_type="period_outstanding event_display_type",
                closing_event_display_type="period_outstanding closing_event_display_type",
                time_period_seconds=10,
            ).dict(),
            {
                "compliance_type": "COMPLIANCE_PERIOD_OUTSTANDING",
                "description": "period_outstanding description",
                "display_name": "period_outstanding display_name",
                "asset_filter": [
                    {"or": ["a", "b"]},
                    {"or": ["x", "z"]},
                ],
                "event_display_type": "period_outstanding event_display_type",
                "closing_event_display_type": "period_outstanding closing_event_display_type",
                "time_period_seconds": 10,
            },
            msg="Incorrect dictionary",
        )

    def test_compliance_policy_dynamic_tolerance(self):
        """
        Test CompliancePolicyDynamicTolerance
        """
        self.assertEqual(
            compliance_policy_requests.CompliancePolicyDynamicTolerance(
                description="dynamic_tolerance description",
                display_name="dynamic_tolerance display_name",
                asset_filter=[
                    ["a", "b"],
                    ["x", "z"],
                ],
                event_display_type="dynamic_tolerance event_display_type",
                closing_event_display_type="dynamic_tolerance closing_event_display_type",
                dynamic_window=86400,
                dynamic_variability=0.5,
            ).dict(),
            {
                "compliance_type": "COMPLIANCE_DYNAMIC_TOLERANCE",
                "description": "dynamic_tolerance description",
                "display_name": "dynamic_tolerance display_name",
                "asset_filter": [
                    {"or": ["a", "b"]},
                    {"or": ["x", "z"]},
                ],
                "event_display_type": "dynamic_tolerance event_display_type",
                "closing_event_display_type": "dynamic_tolerance closing_event_display_type",
                "dynamic_window": 86400,
                "dynamic_variability": 0.5,
            },
            msg="Incorrect dictionary",
        )

    def test_compliance_policy_richness(self):
        """
        Test CompliancePolicyRichness
        """
        self.assertEqual(
            compliance_policy_requests.CompliancePolicyRichness(
                description="richness description",
                display_name="richness display_name",
                asset_filter=[
                    ["a", "b"],
                    ["x", "z"],
                ],
                richness_assertions=[
                    ["rad<7", "weight>5"],
                    ["rad>1", "weight<10"],
                ],
            ).dict(),
            {
                "compliance_type": "COMPLIANCE_RICHNESS",
                "description": "richness description",
                "display_name": "richness display_name",
                "asset_filter": [
                    {"or": ["a", "b"]},
                    {"or": ["x", "z"]},
                ],
                "richness_assertions": [
                    {"or": ["rad<7", "weight>5"]},
                    {"or": ["rad>1", "weight<10"]},
                ],
            },
            msg="Incorrect dictionary",
        )
