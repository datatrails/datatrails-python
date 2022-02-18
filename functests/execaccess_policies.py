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

SELF_SUBJECT = "subjects/00000000-0000-0000-0000-000000000000"

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
        "subjects": [],
        "behaviours": ["Attachments", "RecordEvidence"],
        "include_attributes": [
            "arc_display_name",
            "arc_display_type",
            "arc_firmware_version",
        ],
        "user_attributes": [{"or": ["group:maintainers", "group:supervisors"]}],
    }
]


class TestAccessPoliciesBase(TestCase):
    """
    Test Archivist AccessPolicies Create method
    """

    maxDiff = None

    def setUp(self):
        with open(environ["TEST_AUTHTOKEN_FILENAME"], encoding="utf-8") as fd:
            auth = fd.read().strip()
        self.arch = Archivist(environ["TEST_ARCHIVIST"], auth, verify=False)

        self.props = deepcopy(PROPS)
        self.props["display_name"] = f"{DISPLAY_NAME} {uuid4()}"


class TestAccessPoliciesSimple(TestAccessPoliciesBase):
    """
    Test Archivist AccessPolicies Create method
    """

    maxDiff = None

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
                msg="No access policies found",
            )

    def test_access_policies_count(self):
        """
        Test access_policy count
        """
        count = self.arch.access_policies.count()
        self.assertGreaterEqual(
            count,
            0,
            msg="Count is not zero",
        )


class TestAccessPolicies(TestAccessPoliciesBase):
    """
    Test Archivist AccessPolicies Create method
    """

    maxDiff = None

    def setUp(self):
        super().setUp()
        with open(environ["TEST_AUTHTOKEN_FILENAME_2"], encoding="utf-8") as fd:
            auth_2 = fd.read().strip()
        self.arch_2 = Archivist(environ["TEST_ARCHIVIST"], auth_2, verify=False)

        # creates reciprocal subjects for arch 1 and arch 2.
        self_subject_1 = self.arch.subjects.read(SELF_SUBJECT)
        self_subject_2 = self.arch_2.subjects.read(SELF_SUBJECT)

        subject_1 = self.arch.subjects.create(
            "org2_subject",
            self_subject_2["wallet_pub_key"],
            self_subject_2["tessera_pub_key"],
        )

        subject_2 = self.arch_2.subjects.create(
            "org1_subject",
            self_subject_1["wallet_pub_key"],
            self_subject_1["tessera_pub_key"],
        )

        # check the subjects are confirmed
        self.arch.subjects.wait_for_confirmation(subject_1["identity"])
        self.arch_2.subjects.wait_for_confirmation(subject_2["identity"])

        # modify access_permissions...
        self.access_permissions = deepcopy(ACCESS_PERMISSIONS)
        self.access_permissions[0]["subjects"] = [subject_1["identity"]]

    def test_access_policies_create(self):
        """
        Test access_policy creation
        """
        access_policy = self.arch.access_policies.create(
            self.props,
            FILTERS,
            self.access_permissions,
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
            self.props,
            FILTERS,
            self.access_permissions,
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
            self.props,
            FILTERS,
            self.access_permissions,
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
            msg="Empty access_policy",
        )
