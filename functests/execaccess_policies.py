"""
Test access_policies
"""

from copy import deepcopy
from os import environ
from unittest import TestCase
from uuid import uuid4
from time import sleep

from archivist.archivist import Archivist

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

POLL_FREQUENCY = 10
POLL_INTERVAL = 0.5

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
        "subjects": [],  # empty subjects for now, will be populated in test setup
        "behaviours": ["Attachments", "RecordEvidence"],
        "include_attributes": [
            "arc_display_name",
            "arc_display_type",
            "arc_firmware_version",
        ],
        "user_attributes": [{"or": ["group:maintainers", "group:supervisors"]}],
    }
]


def poll_subject_confirmed(arch, identity):
    """
    polls for the subject to be confirmed for POLL_FREQUENCY every POLL_INTERVAL.

    :raises: AsssertionError if the subject is not confirmed within the polling window.
    """

    for x in range(POLL_FREQUENCY):
        subject = arch.subjects.read(identity)

        if subject["confirmation_status"] == "CONFIRMED":
            return

        sleep(POLL_INTERVAL)

    raise AssertionError(f"subject: {subject['identity']} is not confirmed.")


def reciprocal_subjects(arch_1, arch_2):
    """
    creates reciprocal subjects for arch 1 and arch 2.

    Returns the id's of the imported subjects as a tuple
    """
    self_subject_1 = arch_1.subjects.read(SELF_SUBJECT)
    self_subject_2 = arch_2.subjects.read(SELF_SUBJECT)

    subject_1 = arch_1.subjects.create(
        "org2_subject",
        self_subject_2["wallet_pub_key"],
        self_subject_2["tessera_pub_key"],
    )

    subject_2 = arch_2.subjects.create(
        "org1_subject",
        self_subject_1["wallet_pub_key"],
        self_subject_1["tessera_pub_key"],
    )

    # check the subjects are confirmed
    poll_subject_confirmed(arch_1, subject_1["identity"])
    poll_subject_confirmed(arch_2, subject_2["identity"])

    return subject_1, subject_2


class TestAccessPolicies(TestCase):
    """
    Test Archivist AccessPolicies Create method
    """

    maxDiff = None

    def setUp(self):
        with open(environ["TEST_AUTHTOKEN_FILENAME"], encoding="utf-8") as fd:
            auth = fd.read().strip()
        self.arch = Archivist(environ["TEST_ARCHIVIST"], auth, verify=False)

        with open(environ["TEST_AUTHTOKEN_FILENAME_2"], encoding="utf-8") as fd:
            auth_2 = fd.read().strip()
        self.arch_2 = Archivist(environ["TEST_ARCHIVIST"], auth_2, verify=False)

        self.props = deepcopy(PROPS)
        self.props["display_name"] = f"{DISPLAY_NAME} {uuid4()}"

        # now get reciprocal subjects
        self.subject_id = reciprocal_subjects(self.arch, self.arch_2)[0]
        ACCESS_PERMISSIONS[0]["subjects"] = [self.subject_id["identity"]]

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
