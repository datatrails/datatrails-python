"""
Test access_policies
"""

from copy import deepcopy
from json import dumps as json_dumps
from os import getenv
from time import sleep
from unittest import skipIf
from uuid import uuid4

from archivist.archivist import Archivist
from archivist.constants import ASSET_BEHAVIOURS
from archivist.proof_mechanism import ProofMechanism
from archivist.utils import get_auth

from archivist import logger

from .constants import TestCase

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

DISPLAY_NAME = "AccessPolicy display name"
ARC_DISPLAY_TYPE = "Traffic light with violation camera"
EXT_VENDOR_NAME = "SynsationIndustries"
PROPS = {
    "display_name": DISPLAY_NAME,
    "description": "Policy description",
}
FILTERS = [
    {
        "or": [
            "attributes.arc_namespace=namespace",
        ]
    },
    {
        "or": [
            f"attributes.arc_display_type={ARC_DISPLAY_TYPE}",
        ]
    },
    {
        "or": [
            f"attributes.ext_vendor_name={EXT_VENDOR_NAME}",
        ]
    },
]

BARE_ACCESS_PERMISSIONS = [
    {
        "subjects": [],
        "behaviours": ASSET_BEHAVIOURS,
    }
]
ACCESS_PERMISSIONS = [
    {
        "subjects": [],
        "behaviours": ASSET_BEHAVIOURS,
        "include_attributes": [
            "arc_description",
            "arc_display_name",
            "arc_display_type",
            "arc_firmware_version",
        ],
    },
]

ASSET_NAME = "Telephone with 2 attachments - one bad or not scanned 2022-03-01"
REQUEST_EXISTS_ATTACHMENTS = {
    "selector": [
        {
            "attributes": [
                "arc_display_name",
                "arc_namespace",
            ]
        },
    ],
    "behaviours": ASSET_BEHAVIOURS,
    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
    "attributes": {
        "arc_display_name": ASSET_NAME,
        "arc_namespace": "namespace",
        "arc_firmware_version": "1.0",
        "arc_serial_number": "vtl-x4-07",
        "arc_description": "Traffic flow control light at A603 North East",
        "arc_display_type": ARC_DISPLAY_TYPE,
        "ext_vendor_name": EXT_VENDOR_NAME,
    },
    "attachments": [
        {
            "filename": "functests/test_resources/telephone.jpg",
            "content_type": "image/jpg",
        },
        {
            "url": "https://secure.eicar.org/eicarcom2.zip",
            "content_type": "application/zip",
        },
    ],
}

if getenv("RKVST_LOGLEVEL") is not None:
    logger.set_logger(getenv("RKVST_LOGLEVEL"))

LOGGER = logger.LOGGER


class TestAccessPoliciesBase(TestCase):
    """
    Test Archivist AccessPolicies Create method
    """

    maxDiff = None

    def setUp(self):
        auth = get_auth(
            auth_token=getenv("RKVST_AUTHTOKEN"),
            auth_token_filename=getenv("RKVST_AUTHTOKEN_FILENAME"),
            client_id=getenv("RKVST_APPREG_CLIENT"),
            client_secret=getenv("RKVST_APPREG_SECRET"),
            client_secret_filename=getenv("RKVST_APPREG_SECRET_FILENAME"),
        )
        self.arch = Archivist(getenv("RKVST_URL"), auth, verify=False)

        # these are for access_policies
        self.ac_props = deepcopy(PROPS)
        self.ac_props["display_name"] = f"{DISPLAY_NAME} {uuid4()}"

        self.ac_access_permissions = deepcopy(ACCESS_PERMISSIONS)

    def tearDown(self):
        self.ac_access_permissions = None
        self.ac_props = None
        self.arch.close()


class TestAccessPoliciesSimple(TestAccessPoliciesBase):
    """
    Test Archivist AccessPolicies Create method
    """

    maxDiff = None

    def test_access_policies_list(self):
        """
        Test access_policy list
        """
        for idx in range(3):
            access_policy = self.arch.access_policies.create(
                self.ac_props,
                FILTERS,
                self.ac_access_permissions,
            )
            self.assertEqual(
                access_policy["display_name"],
                self.ac_props["display_name"],
                msg="Incorrect display name",
            )

        count = self.arch.access_policies.count(
            display_name=self.ac_props["display_name"]
        )
        self.assertEqual(
            count,
            3,
            msg="Count is incorrect",
        )
        access_policies = self.arch.access_policies.list(
            display_name=self.ac_props["display_name"]
        )
        for access_policy in access_policies:
            self.assertEqual(
                access_policy["display_name"],
                self.ac_props["display_name"],
                msg="Incorrect display name",
            )
            self.assertGreater(
                len(access_policy["display_name"]),
                0,
                msg="Illegal display name",
            )
            self.arch.access_policies.delete(
                access_policy["identity"],
            )

    def test_access_policies_create(self):
        """
        Test access_policy creation
        """
        access_policy = self.arch.access_policies.create(
            self.ac_props,
            FILTERS,
            self.ac_access_permissions,
        )
        self.assertEqual(
            access_policy["display_name"],
            self.ac_props["display_name"],
            msg="Incorrect display name",
        )
        self.arch.access_policies.delete(
            access_policy["identity"],
        )

    def test_access_policies_update(self):
        """
        Test access_policy update
        """
        access_policy = self.arch.access_policies.create(
            self.ac_props,
            FILTERS,
            self.ac_access_permissions,
        )
        self.assertEqual(
            access_policy["display_name"],
            self.ac_props["display_name"],
            msg="Incorrect display name",
        )
        access_policy = self.arch.access_policies.update(
            access_policy["identity"],
            props=self.ac_props,
            filters=FILTERS,
            access_permissions=ACCESS_PERMISSIONS,
        )
        self.arch.access_policies.delete(
            access_policy["identity"],
        )

    def test_access_policies_delete(self):
        """
        Test access_policy delete
        """
        access_policy = self.arch.access_policies.create(
            self.ac_props,
            FILTERS,
            self.ac_access_permissions,
        )
        self.assertEqual(
            access_policy["display_name"],
            self.ac_props["display_name"],
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


# Specified permissions with expected results
TESTDATA = [
    {
        "name": "include_attributes",
        "permission": {
            "include_attributes": [
                "arc_description",
                "arc_display_name",
                "arc_display_type",
                "arc_firmware_version",
            ],
        },
        "expected": {
            "arc_display_name": "Org1 asset",
            "arc_display_type": "Traffic light with violation camera",
            "arc_firmware_version": "1.0",
            "arc_description": "Traffic flow control light at A603 North East",
        },
    },
    {
        "name": "asset_attributes_read",
        "permission": {
            "asset_attributes_read": [
                "arc_display_name",
                "arc_display_type",
                "arc_firmware_version",
            ],
        },
        "expected": {
            "arc_display_name": "Org1 asset",
            "arc_display_type": "Traffic light with violation camera",
            "arc_firmware_version": "1.0",
        },
    },
]


@skipIf(
    getenv("RKVST_AUTHTOKEN_FILENAME_2") is None,
    "cannot run test as RKVST_AUTHTOKEN_FILENAME_2 is not set",
)
class TestAccessPoliciesShare(TestAccessPoliciesBase):
    """
    Test Archivist AccessPolicies sharing
    """

    maxDiff = None

    def setUp(self):
        super().setUp()
        with open(getenv("RKVST_AUTHTOKEN_FILENAME_2"), encoding="utf-8") as fd:
            auth_2 = fd.read().strip()
        self.arch_2 = Archivist(getenv("RKVST_URL"), auth_2, verify=False)

        # creates reciprocal subjects for arch 1 and arch 2.
        # subject 1 contains details of subject 2 to be shared
        self.subject_1, self.subject_2 = self.arch.subjects.share(
            "org2_subject",
            "org1_subject",
            self.arch_2,
        )
        LOGGER.debug()
        LOGGER.debug("Org1: subject_1 %s", json_dumps(self.subject_1, indent=4))
        LOGGER.debug("Org2: subject_2 %s", json_dumps(self.subject_2, indent=4))

    def tearDown(self):
        super().tearDown()
        self.arch_2.close()

    def _create_asset(self, label, arch, uuid):
        asset_data = deepcopy(REQUEST_EXISTS_ATTACHMENTS)
        asset_data["attributes"]["arc_namespace"] = uuid
        asset_data["attributes"]["arc_display_name"] = f"{label} asset"
        asset, existed = arch.assets.create_if_not_exists(
            asset_data,
            confirm=True,
        )
        LOGGER.debug(label, ": asset %s", json_dumps(asset, indent=4))
        LOGGER.debug(label, ": existed %s", existed)
        return asset

    def _create_access_policy(self, label, arch, uuid, subject, testdata):
        access_permissions = deepcopy(BARE_ACCESS_PERMISSIONS)
        access_permissions[0]["subjects"] = [
            subject["identity"],
        ]
        for k, v in testdata["permission"].items():
            access_permissions[0][k] = v

        ac_props = deepcopy(PROPS)
        ac_props["display_name"] = f"{DISPLAY_NAME} {uuid}"

        filters = deepcopy(FILTERS)
        filters[0]["or"][0] = f"attributes.arc_namespace={uuid}"
        access_policy = arch.access_policies.create(
            ac_props,
            filters,
            access_permissions,
        )
        self.assertEqual(
            access_policy["display_name"],
            ac_props["display_name"],
            msg="Incorrect display name",
        )
        LOGGER.debug(label, ": access_policy %s", json_dumps(access_policy, indent=4))
        return access_policy

    def _list_matching_assets(self, label, arch, assets, expected_asset, access_policy):
        for idx, asset in enumerate(
            arch.access_policies.list_matching_assets(access_policy["identity"])
        ):
            title = assets.get(asset["identity"])
            # only deal with assets created during this test
            if title:
                LOGGER.debug("%s: %d Matching asse:t %s", label, idx, title)
                LOGGER.debug(
                    "%s: %d Matching asse:t %s", label, idx, json_dumps(asset, indent=4)
                )
                self.assertEqual(
                    expected_asset["identity"],
                    asset["identity"],
                    msg="Incorrect asset",
                )

    def _list_matching_access_policies(
        self, label, arch, access_policies, expected_access_policy, asset
    ):
        for idx, access_policy in enumerate(
            arch.access_policies.list_matching_access_policies(asset["identity"])
        ):
            title = access_policies.get(access_policy["identity"])
            # only deal with access_policies created during this test
            if title:
                LOGGER.debug("%s: %d: Matching access policy: %s", label, idx, title)
                LOGGER.debug(
                    "%s: %d: Matching access policy: %s",
                    label,
                    idx,
                    json_dumps(access_policy, indent=4),
                )
                self.assertEqual(
                    expected_access_policy["identity"],
                    access_policy["identity"],
                    msg="Incorrect access_policy",
                )

    def test_access_policies_share_assets_symmetrically(self):
        """
        Test access_policy share asset between 2 tokens/organisations/tenants
        """
        testdata = TESTDATA[0]
        LOGGER.debug()
        assets = {}  # maps identity to name
        access_policies = {}  # maps identity to name
        uuid = str(uuid4())  # stamps assets and access policies as unique

        LOGGER.debug("1. create unique org1 asset and access_policy")
        org1_asset = self._create_asset("Org1", self.arch, uuid)
        assets[org1_asset["identity"]] = "org1_asset"

        org1_access_policy = self._create_access_policy(
            "Org1", self.arch, uuid, self.subject_1, testdata
        )
        access_policies[org1_access_policy["identity"]] = "org1_access_policy"

        LOGGER.debug("2. create org2 asset and access_policy")
        org2_asset = self._create_asset("Org2", self.arch_2, uuid)
        assets[org2_asset["identity"]] = "org2_asset"

        org2_access_policy = self._create_access_policy(
            "Org2", self.arch_2, uuid, self.subject_2, testdata
        )
        access_policies[org2_access_policy["identity"]] = "org2_access_policy"

        LOGGER.debug("3. First org - list matching assets")
        self._list_matching_assets(
            "Org1", self.arch, assets, org1_asset, org1_access_policy
        )

        LOGGER.debug("4. First org - list matching access policies")
        self._list_matching_access_policies(
            "Org1", self.arch, access_policies, org1_access_policy, org1_asset
        )

        LOGGER.debug("5. Second org - list matching assets")
        self._list_matching_assets(
            "Org2", self.arch_2, assets, org2_asset, org2_access_policy
        )

        LOGGER.debug("6. Second org - list matching access policies")
        self._list_matching_access_policies(
            "Org2", self.arch_2, access_policies, org2_access_policy, org2_asset
        )

        LOGGER.debug("7. First org - read asset from second org")
        asset = self.arch.assets.read(org2_asset["identity"])
        LOGGER.debug("Org1: asset %s", json_dumps(asset, indent=4))

        LOGGER.debug("8. Second org - read asset from first org")
        asset = self.arch_2.assets.read(org1_asset["identity"])
        LOGGER.debug("Org2: asset %s", json_dumps(asset, indent=4))

        self.arch.access_policies.delete(
            org1_access_policy["identity"],
        )
        self.arch_2.access_policies.delete(
            org2_access_policy["identity"],
        )

    def test_access_policies_share_asset_with_different_attributes(self):
        """
        Test access_policy share asset between 2 tokens/organisations/tenants
        """
        for idx, testdata in enumerate(TESTDATA):
            with self.subTest(testdata["name"], idx=idx):
                LOGGER.debug()
                assets = {}  # maps identity to name
                access_policies = {}  # maps identity to name
                uuid = str(uuid4())  # stamps assets and access policies as unique

                LOGGER.debug("1. create unique org1 asset and access_policy")
                org1_asset = self._create_asset("Org1", self.arch, uuid)
                assets[org1_asset["identity"]] = "org1_asset"

                org1_access_policy = self._create_access_policy(
                    "Org1", self.arch, uuid, self.subject_1, testdata
                )
                access_policies[org1_access_policy["identity"]] = "org1_access_policy"

                sleep(2)  # let the access policy become available

                LOGGER.debug("2. read org1 asset from org2")
                asset = self.arch_2.assets.read(org1_asset["identity"])
                LOGGER.debug("Org2: asset %s", json_dumps(asset, indent=4))
                LOGGER.debug(
                    "Org2: expected %s", json_dumps(testdata["expected"], indent=4)
                )
                LOGGER.debug(
                    "Org2: attributes %s", json_dumps(asset["attributes"], indent=4)
                )
                self.assertEqual(
                    testdata["expected"],
                    asset["attributes"],
                    msg="Incorrect attributes",
                )
                self.arch.access_policies.delete(
                    org1_access_policy["identity"],
                )
