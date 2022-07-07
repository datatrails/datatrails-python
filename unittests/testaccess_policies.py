"""
Test access policies
"""

from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ASSET_BEHAVIOURS,
    ROOT,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ACCESS_POLICIES_SUBPATH,
    ACCESS_POLICIES_LABEL,
    ASSETS_LABEL,
)
from archivist.errors import ArchivistBadRequestError

from .mock_response import MockResponse
from .testassets import RESPONSE as ASSET


# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

ACCESS_POLICY_NAME = "Policy display name"
PROPS = {
    "display_name": ACCESS_POLICY_NAME,
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
        "behaviours": ASSET_BEHAVIOURS,
        "include_attributes": [
            "arc_display_name",
            "arc_display_type",
            "arc_firmware_version",
        ],
        "user_attributes": [{"or": ["group:maintainers", "group:supervisors"]}],
    }
]

IDENTITY = f"{ACCESS_POLICIES_LABEL}/xxxxxxxx"
SUBPATH = f"{ACCESS_POLICIES_SUBPATH}/{ACCESS_POLICIES_LABEL}"
ASSET_ID = f"{ASSETS_LABEL}/yyyyyyyy"

RESPONSE = {
    **PROPS,
    "identity": IDENTITY,
    "filters": FILTERS,
    "access_permissions": ACCESS_PERMISSIONS,
}
REQUEST = {
    **PROPS,
    "filters": FILTERS,
    "access_permissions": ACCESS_PERMISSIONS,
}


class TestAccessPolicies(TestCase):
    """
    Test Archivist AccessPolicies Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()

    def test_access_policies_str(self):
        """
        Test access_policy str
        """
        self.assertEqual(
            str(self.arch.access_policies),
            "AccessPoliciesClient(url)",
            msg="Incorrect str",
        )

    def test_access_policies_create(self):
        """
        Test access_policy creation
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            access_policy = self.arch.access_policies.create(
                PROPS, FILTERS, ACCESS_PERMISSIONS
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBPATH}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="CREATE method called incorrectly",
            )
            self.assertEqual(
                access_policy,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )
            self.assertEqual(
                access_policy.name,
                ACCESS_POLICY_NAME,
                msg="Incorrect name property",
            )

    def test_access_policies_read(self):
        """
        Test access_policy reading
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            access_policy = self.arch.access_policies.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{IDENTITY}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                        "params": None,
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_access_policies_delete(self):
        """
        Test access_policy deleting
        """
        with mock.patch.object(self.arch.session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(200, {})

            access_policy = self.arch.access_policies.delete(IDENTITY)
            self.assertEqual(
                tuple(mock_delete.call_args),
                (
                    ((f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{IDENTITY}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                    },
                ),
                msg="DELETE method called incorrectly",
            )

    def test_access_policies_update(self):
        """
        Test access_policy deleting
        """
        with mock.patch.object(self.arch.session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(200, **RESPONSE)

            access_policy = self.arch.access_policies.update(
                IDENTITY,
                props=PROPS,
            )
            args, kwargs = mock_patch.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{IDENTITY}",),
                msg="PATCH method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": PROPS,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="PATCH method kwargs called incorrectly",
            )

    def test_access_policies_read_with_error(self):
        """
        Test read method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(400)
            with self.assertRaises(ArchivistBadRequestError):
                resp = self.arch.access_policies.read(IDENTITY)

    def test_access_policies_count(self):
        """
        Test access_policy counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                access_policies=[
                    RESPONSE,
                ],
            )

            count = self.arch.access_policies.count()
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (f"url/{ROOT}/{SUBPATH}",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {"page_size": 1},
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )
            self.assertEqual(
                count,
                1,
                msg="Incorrect count",
            )

    def test_access_policies_count_by_name(self):
        """
        Test access_policy counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                access_policies=[
                    RESPONSE,
                ],
            )

            count = self.arch.access_policies.count(
                display_name="Policy display name",
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "page_size": 1,
                            "display_name": "Policy display name",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_access_policies_list(self):
        """
        Test access_policy listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                access_policies=[
                    RESPONSE,
                ],
            )

            access_policies = list(self.arch.access_policies.list())
            self.assertEqual(
                len(access_policies),
                1,
                msg="incorrect number of access_policies",
            )
            for access_policy in access_policies:
                self.assertEqual(
                    access_policy,
                    RESPONSE,
                    msg="Incorrect access_policy listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/{SUBPATH}",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": None,
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_access_policies_list_by_name(self):
        """
        Test access_policy listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                access_policies=[
                    RESPONSE,
                ],
            )

            access_policies = list(
                self.arch.access_policies.list(
                    display_name="Policy display name",
                )
            )
            self.assertEqual(
                len(access_policies),
                1,
                msg="incorrect number of access_policies",
            )
            for access_policy in access_policies:
                self.assertEqual(
                    access_policy,
                    RESPONSE,
                    msg="Incorrect access_policy listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        ((f"url/{ROOT}/{SUBPATH}"),),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {"display_name": "Policy display name"},
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_access_policies_list_matching_access_policies(self):
        """
        Test access_policy counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                access_policies=[
                    RESPONSE,
                ],
            )
            access_policies = list(
                self.arch.access_policies.list_matching_access_policies(ASSET_ID)
            )
            self.assertEqual(
                len(access_policies),
                1,
                msg="incorrect number of access_policies",
            )
            for access_policy in access_policies:
                self.assertEqual(
                    access_policy,
                    RESPONSE,
                    msg="Incorrect access_policy listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            f"url/{ROOT}/"
                            f"{ACCESS_POLICIES_SUBPATH}/{ASSET_ID}/{ACCESS_POLICIES_LABEL}",
                        ),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": None,
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_access_policies_list_matching_assets(self):
        """
        Test access_policy counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                assets=[
                    ASSET,
                ],
            )
            assets = list(self.arch.access_policies.list_matching_assets(IDENTITY))
            self.assertEqual(
                len(assets),
                1,
                msg="incorrect number of assets",
            )
            for asset in assets:
                self.assertEqual(
                    asset,
                    ASSET,
                    msg="Incorrect asset listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{IDENTITY}/{ASSETS_LABEL}",
                        ),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": None,
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )
