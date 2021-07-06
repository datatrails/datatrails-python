"""
Test access_policies
"""

from copy import deepcopy
from os import environ
from unittest import TestCase
from uuid import uuid4

from archivist.archivist import Archivist

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

DISPLAY_NAME = "AccessPolicy display name"
PROPS = {
    "display_name": DISPLAY_NAME,
    "description": "Policy description",
}
FILTERS = [
    {
        "or": [
            "attributes.arc_home_location_identity=locations/5ea815f0-4de1-4a84-9377-701e880fe8ae",
            "attributes.arc_home_location_identity=locations/27eed70b-9e2b-4db1-b8c4-e36505350dcc",
        ]
    },
    {
        "or": [
            "attributes.arc_display_type=Valve",
            "attributes.arc_display_type=Pump",
        ]
    },
    {
        "or": [
            "attributes.ext_vendor_name=SynsationIndustries",
        ]
    },
]

ACCESS_PERMISSIONS = [
    {
        "subjects": [
            "subjects/6a951b62-0a26-4c22-a886-1082297b063b",
            "subjects/a24306e5-dc06-41ba-a7d6-2b6b3e1df48d",
        ],
        "behaviours": ["Attachments", "RecordEvidence"],
        "include_attributes": [
            "arc_display_name",
            "arc_display_type",
            "arc_firmware_version",
        ],
        "user_attributes": [{"or": ["group:maintainers", "group:supervisors"]}],
    }
]


class TestAccessPolicies(TestCase):
    """
    Test Archivist AccessPolicies Create method
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        with open(environ["TEST_AUTHTOKEN"]) as fd:
            auth = fd.read().strip()
        cls.arch = Archivist(environ["TEST_ARCHIVIST"], auth=auth, verify=False)
        cls.props = deepcopy(PROPS)
        cls.props["display_name"] = f"{DISPLAY_NAME} {uuid4()}"

    def test_access_policies_create(self):
        """
        Test access_policy creation
        """
        access_policy = self.arch.access_policies.create(
            self.props, FILTERS, ACCESS_PERMISSIONS
        )
        self.assertEqual(
            access_policy["display_name"],
            self.props["display_name"],
            msg="Incorrect display name",
        )

    def test_access_policies_update(self):
        """
        Test access_policy update
        """
        access_policy = self.arch.access_policies.create(
            self.props, FILTERS, ACCESS_PERMISSIONS
        )
        self.assertEqual(
            access_policy["display_name"],
            self.props["display_name"],
            msg="Incorrect display name",
        )
        access_policy = self.arch.access_policies.update(
            access_policy["identity"],
            props=self.props,
            filters=FILTERS,
            access_permissions=ACCESS_PERMISSIONS,
        )

    def test_access_policies_delete(self):
        """
        Test access_policy delete
        """
        access_policy = self.arch.access_policies.create(
            self.props, FILTERS, ACCESS_PERMISSIONS
        )
        self.assertEqual(
            access_policy["display_name"],
            self.props["display_name"],
            msg="Incorrect display name",
        )
        access_policy = self.arch.access_policies.delete(
            access_policy["identity"],
        )
        self.assertEqual(
            access_policy,
            {},
            msg="Incorrect access_policy",
        )

    def test_access_policies_list(self):
        """
        Test access_policy list
        """
        # TODO: filtering on display_name does not currently work...
        access_policies = self.arch.access_policies.list(
            display_name=self.props["display_name"]
        )
        for access_policy in access_policies:
            self.assertEqual(
                access_policy["display_name"],
                self.props["display_name"],
                msg="Incorrect display name",
            )
            self.assertGreater(
                len(access_policy["display_name"]),
                0,
                msg="Incorrect display name",
            )

    def test_access_policies_count(self):
        """
        Test access_policy count
        """
        count = self.arch.access_policies.count()
        self.assertGreaterEqual(
            count,
            0,
            msg="Count is zero",
        )
