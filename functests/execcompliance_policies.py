"""
Test compliance policies
"""
from json import dumps as json_dumps
from os import getenv
from time import sleep
from unittest import TestCase
from uuid import uuid4

from archivist.archivist import Archivist
from archivist.compliance_policy_requests import (
    CompliancePolicyCurrentOutstanding,
    CompliancePolicyDynamicTolerance,
    CompliancePolicyPeriodOutstanding,
    CompliancePolicyRichness,
    CompliancePolicySince,
)
from archivist.compliance_policy_type import CompliancePolicyType
from archivist.utils import get_auth

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

from archivist import logger

if getenv("TEST_DEBUG") is not None:
    logger.set_logger(getenv("TEST_DEBUG"))
else:
    logger.set_logger("INFO")

LOGGER = logger.LOGGER

# Ridiculaously short maintenance period for test purposes
SINCE_POLICY = CompliancePolicySince(
    description="Maintenance should be performed every 10 seconds",
    display_name="Regular Maintenance of Traffic light",
    asset_filter=[
        ["attributes.arc_display_type=Traffic Light"],
    ],
    event_display_type="Maintenance Performed",
    time_period_seconds=10,  # very short so we can test
)

CURRENT_OUTSTANDING_POLICY = CompliancePolicyCurrentOutstanding(
    description="Maintenance should be performed every 10 seconds",
    display_name="Regular Maintenance of Traffic light",
    asset_filter=[
        ["attributes.arc_display_type=Traffic Light"],
    ],
    event_display_type="Maintenance Request",
    closing_event_display_type="Maintenance Performed",
)

PERIOD_OUTSTANDING_POLICY = CompliancePolicyPeriodOutstanding(
    description="period_outstanding description",
    display_name="period_outstanding display_name",
    asset_filter=[
        ["attributes.radioactive=true"],
    ],
    event_display_type="period_outstanding event_display_type",
    closing_event_display_type="period_outstanding closing_event_display_type",
    time_period_seconds=10,
)
DYNAMIC_TOLERANCE_POLICY = CompliancePolicyDynamicTolerance(
    description="dynamic_tolerance description",
    display_name="dynamic_tolerance display_name",
    asset_filter=[
        ["attributes.radioactive=true"],
    ],
    event_display_type="dynamic_tolerance event_display_type",
    closing_event_display_type="dynamic_tolerance closing_event_display_type",
    dynamic_window=86400,
    dynamic_variability=0.5,
)
RICHNESS_POLICY = CompliancePolicyRichness(
    description="richness description",
    display_name="richness display_name",
    asset_filter=[
        ["attributes.radioactive=true"],
    ],
    richness_assertions=[
        ["rad<7"],
    ],
)


class TestCompliancePoliciesBase(TestCase):
    """
    Test Archivist CompliancePolicies Create method
    """

    maxDiff = None

    def setUp(self):
        auth = get_auth(
            auth_token_filename=getenv("TEST_AUTHTOKEN_FILENAME"),
            client_id=getenv("TEST_CLIENT_ID"),
            client_secret=getenv("TEST_CLIENT_SECRET"),
            client_secret_filename=getenv("TEST_CLIENT_SECRET_FILENAME"),
        )
        self.arch = Archivist(getenv("TEST_ARCHIVIST"), auth, verify=False)
        print()


class TestCompliancePolicies(TestCompliancePoliciesBase):
    def test_compliancepolicies_create_since(self):
        """
        Test compliance_policies creation
        """
        compliance_policy = self.arch.compliance_policies.create(
            SINCE_POLICY,
        )
        self.assertEqual(
            compliance_policy["display_name"],
            SINCE_POLICY.display_name,
            msg="Incorrect display name",
        )
        print("SINCE_POLICY:", json_dumps(compliance_policy, indent=4))
        self.arch.compliance_policies.delete(
            compliance_policy["identity"],
        )

    def test_compliancepolicies_create_richness(self):
        """
        Test compliance_policies creation
        """
        compliance_policy = self.arch.compliance_policies.create(
            RICHNESS_POLICY,
        )
        self.assertEqual(
            compliance_policy["display_name"],
            RICHNESS_POLICY.display_name,
            msg="Incorrect display name",
        )
        print("RICHNESS_POLICY:", json_dumps(compliance_policy, indent=4))
        self.arch.compliance_policies.delete(
            compliance_policy["identity"],
        )

    def test_compliancepolicies_create_dynamic_tolerance(self):
        """
        Test compliance_policies creation
        """
        compliance_policy = self.arch.compliance_policies.create(
            DYNAMIC_TOLERANCE_POLICY,
        )
        self.assertEqual(
            compliance_policy["display_name"],
            DYNAMIC_TOLERANCE_POLICY.display_name,
            msg="Incorrect display name",
        )
        print("DYNAMIC_TOLERANCE_POLICY:", json_dumps(compliance_policy, indent=4))
        self.arch.compliance_policies.delete(
            compliance_policy["identity"],
        )

    def test_compliancepolicies_create_current_outstanding(self):
        """
        Test compliance_policies creation
        """
        compliance_policy = self.arch.compliance_policies.create(
            CURRENT_OUTSTANDING_POLICY,
        )
        self.assertEqual(
            compliance_policy["display_name"],
            CURRENT_OUTSTANDING_POLICY.display_name,
            msg="Incorrect display name",
        )
        print("CURRENT_OUTSTANDING_POLICY:", json_dumps(compliance_policy, indent=4))
        self.arch.compliance_policies.delete(
            compliance_policy["identity"],
        )

    def test_compliancepolicies_create_period_understanding(self):
        """
        Test compliance_policies creation
        """
        compliance_policy = self.arch.compliance_policies.create(
            PERIOD_OUTSTANDING_POLICY,
        )
        self.assertEqual(
            compliance_policy["display_name"],
            PERIOD_OUTSTANDING_POLICY.display_name,
            msg="Incorrect display name",
        )
        print("PERIOD_OUTSTANDING_POLICY:", json_dumps(compliance_policy, indent=4))
        self.arch.compliance_policies.delete(
            compliance_policy["identity"],
        )

    def test_compliance_policies_list(self):
        """
        Test compliance_policy list
        """
        compliance_policies = list(self.arch.compliance_policies.list())
        for i, compliance_policy in enumerate(compliance_policies):
            print(i, ":", json_dumps(compliance_policy, indent=4))
            self.assertGreater(
                len(compliance_policy["display_name"]),
                0,
                msg="Incorrect display name",
            )
            self.arch.compliance_policies.delete(
                compliance_policy["identity"],
            )

    def test_compliance_policies_count(self):
        """
        Test compliance_policy count
        """
        count = self.arch.compliance_policies.count(
            props={"compliance_type": CompliancePolicyType.COMPLIANCE_SINCE.name}
        )
        print("No. of 'SINCE' compliance policies:", count)
        count = self.arch.compliance_policies.count(
            props={"compliance_type": CompliancePolicyType.COMPLIANCE_RICHNESS.name}
        )
        print("No. of 'RICHNESS' compliance policies:", count)
        count = self.arch.compliance_policies.count(
            props={
                "compliance_type": CompliancePolicyType.COMPLIANCE_DYNAMIC_TOLERANCE.name
            }
        )
        print("No. of 'DYNAMIC_TOLERANCE' compliance policies:", count)
        count = self.arch.compliance_policies.count(
            props={
                "compliance_type": CompliancePolicyType.COMPLIANCE_CURRENT_OUTSTANDING.name
            }
        )
        print("No. of 'CURRENT_OUTSTANDING' compliance policies:", count)
        count = self.arch.compliance_policies.count(
            props={
                "compliance_type": CompliancePolicyType.COMPLIANCE_PERIOD_OUTSTANDING.name
            }
        )
        print("No. of 'PERIOD_OUTSTANDING' compliance policies:", count)


TRAFFIC_LIGHT = {
    "arc_display_name": "Traffic light model 54",
    "arc_description": "Traffic flow control light at A603 North East",
    "arc_display_type": "Traffic Light",
}

PROPS = {
    "operation": "Record",
    "behaviour": "RecordEvidence",
}


class TestCompliancePoliciesCompliantAt(TestCompliancePoliciesBase):
    def test_compliancepolicies_since(self):
        """
        Test compliance_policies creation
        """
        tag = uuid4()
        compliance_policy = self.arch.compliance_policies.create(
            CompliancePolicySince(
                description="Maintenance should be performed every 10 seconds",
                display_name="Regular Maintenance of Traffic light",
                asset_filter=[
                    ["attributes.arc_display_type=Traffic Light"],
                ],
                event_display_type=f"Maintenance Performed {tag}",
                time_period_seconds=10,  # very short so we can test
            )
        )
        print("SINCE_POLICY:", json_dumps(compliance_policy, indent=4))

        traffic_light = self.arch.assets.create(
            attrs=TRAFFIC_LIGHT,
            confirm=True,
        )
        print("TRAFFIC_LIGHT:", json_dumps(traffic_light, indent=4))

        maintenance_performed = self.arch.events.create(
            traffic_light["identity"],
            PROPS,
            {
                "arc_description": "Maintenance performed on traffic light",
                "arc_display_type": f"Maintenance Performed {tag}",
            },
            confirm=True,
        )
        print("MAINTENANCE_PERFORMED:", json_dumps(maintenance_performed, indent=4))

        print("Sleep 1 second...")
        sleep(1)
        compliance = self.arch.compliance.compliant_at(
            traffic_light["identity"],
        )
        print("COMPLIANCE (true):", json_dumps(compliance, indent=4))
        self.assertTrue(
            compliance["compliant"],
            msg="Assets should be compliant",
        )

        print("Sleep 15 seconds...")
        sleep(15)
        compliance = self.arch.compliance.compliant_at(
            traffic_light["identity"],
        )
        print("COMPLIANCE (false):", json_dumps(compliance, indent=4))
        self.assertFalse(
            compliance["compliant"],
            msg="Assets should not be compliant",
        )

        compliance_policy = self.arch.compliance_policies.delete(
            compliance_policy["identity"],
        )

    def test_compliancepolicies_current_outstanding(self):
        """
        Test compliance_policies creation
        """
        tag = uuid4()
        compliance_policy = self.arch.compliance_policies.create(
            CompliancePolicyCurrentOutstanding(
                description="Maintenance should be completed",
                display_name="Regular Maintenance of Traffic light",
                asset_filter=[
                    ["attributes.arc_display_type=Traffic Light"],
                ],
                event_display_type=f"Maintenance Request {tag}",
                closing_event_display_type=f"Maintenance Performed {tag}",
            ),
        )
        print("CURRENT_OUTSTANDING_POLICY:", json_dumps(compliance_policy, indent=4))

        traffic_light = self.arch.assets.create(
            attrs=TRAFFIC_LIGHT,
            confirm=True,
        )
        print("TRAFFIC_LIGHT:", json_dumps(traffic_light, indent=4))

        maintenance_request = self.arch.events.create(
            traffic_light["identity"],
            PROPS,
            {
                "arc_description": "Maintenance request on traffic light",
                "arc_display_type": f"Maintenance Request {tag}",
                "arc_correlation_value": str(tag),
            },
            confirm=True,
        )
        print("MAINTENANCE_REQUIRED:", json_dumps(maintenance_request, indent=4))

        print("Sleep 1 second...")
        sleep(1)

        compliance = self.arch.compliance.compliant_at(
            traffic_light["identity"],
        )
        print("COMPLIANCE (false):", json_dumps(compliance, indent=4))
        self.assertFalse(
            compliance["compliant"],
            msg="Assets should not be compliant",
        )

        maintenance_performed = self.arch.events.create(
            traffic_light["identity"],
            PROPS,
            {
                "arc_description": "Maintenance performed on traffic light",
                "arc_display_type": f"Maintenance Performed {tag}",
                "arc_correlation_value": str(tag),
            },
            confirm=True,
        )
        print("MAINTENANCE_PERFORMED:", json_dumps(maintenance_performed, indent=4))

        print("Sleep 1 second...")
        sleep(1)

        compliance = self.arch.compliance.compliant_at(
            traffic_light["identity"],
        )
        print("COMPLIANCE (true):", json_dumps(compliance, indent=4))
        self.assertTrue(
            compliance["compliant"],
            msg="Assets should be compliant",
        )

        compliance_policy = self.arch.compliance_policies.delete(
            compliance_policy["identity"],
        )
