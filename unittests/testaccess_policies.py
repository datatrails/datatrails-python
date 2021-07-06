"""
Test access policies
"""

import json
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ACCESS_POLICIES_SUBPATH,
    ACCESS_POLICIES_LABEL,
    ASSETS_LABEL,
)
from archivist.errors import ArchivistBadRequestError
from archivist.access_policies import DEFAULT_PAGE_SIZE

from .mock_response import MockResponse
from .testassets import RESPONSE as ASSET


# pylint: disable=missing-docstring
# pylint: disable=unused-variable

PROPS = {
    "display_name": "Policy display name",
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
REQUEST_DATA = json.dumps(REQUEST)
UPDATE_DATA = json.dumps(PROPS)


class TestAccessPolicies(TestCase):
    """
    Test Archivist AccessPolicies Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", auth="authauthauth")

    @mock.patch("requests.post")
    def test_access_policies_create(self, mock_post):
        """
        Test access_policy creation
        """
        mock_post.return_value = MockResponse(200, **RESPONSE)

        access_policy = self.arch.access_policies.create(
            PROPS, FILTERS, ACCESS_PERMISSIONS
        )
        self.assertEqual(
            tuple(mock_post.call_args),
            (
                ((f"url/{ROOT}/{SUBPATH}"),),
                {
                    "data": REQUEST_DATA,
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="CREATE method called incorrectly",
        )
        self.assertEqual(
            access_policy,
            RESPONSE,
            msg="CREATE method called incorrectly",
        )

    @mock.patch("requests.get")
    def test_access_policies_read(self, mock_get):
        """
        Test access_policy reading
        """
        mock_get.return_value = MockResponse(200, **RESPONSE)

        access_policy = self.arch.access_policies.read(IDENTITY)
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                ((f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{IDENTITY}"),),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="GET method called incorrectly",
        )

    @mock.patch("requests.delete")
    def test_access_policies_delete(self, mock_delete):
        """
        Test access_policy deleting
        """
        mock_delete.return_value = MockResponse(200, {})

        access_policy = self.arch.access_policies.delete(IDENTITY)
        self.assertEqual(
            tuple(mock_delete.call_args),
            (
                ((f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{IDENTITY}"),),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="DELETE method called incorrectly",
        )

    @mock.patch("requests.patch")
    def test_access_policies_update(self, mock_patch):
        """
        Test access_policy deleting
        """
        mock_patch.return_value = MockResponse(200, **RESPONSE)

        access_policy = self.arch.access_policies.update(
            IDENTITY,
            PROPS,
        )
        self.assertEqual(
            tuple(mock_patch.call_args),
            (
                ((f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{IDENTITY}"),),
                {
                    "data": UPDATE_DATA,
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="PATCH method called incorrectly",
        )

    @mock.patch("requests.get")
    def test_access_policies_read_with_error(self, mock_get):
        """
        Test read method with error
        """
        mock_get.return_value = MockResponse(400)
        with self.assertRaises(ArchivistBadRequestError):
            resp = self.arch.access_policies.read(IDENTITY)

    @mock.patch("requests.get")
    def test_access_policies_count(self, mock_get):
        """
        Test access_policy counting
        """
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
                ((f"url/{ROOT}/{SUBPATH}" "?page_size=1"),),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: "true",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="GET method called incorrectly",
        )
        self.assertEqual(
            count,
            1,
            msg="Incorrect count",
        )

    @mock.patch("requests.get")
    def test_access_policies_count_by_name(self, mock_get):
        """
        Test access_policy counting
        """
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
                (
                    (
                        f"url/{ROOT}/{SUBPATH}"
                        "?page_size=1"
                        "&display_name=Policy display name"
                    ),
                ),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: "true",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="GET method called incorrectly",
        )

    @mock.patch("requests.get")
    def test_access_policies_list(self, mock_get):
        """
        Test access_policy listing
        """
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
                    (f"url/{ROOT}/{SUBPATH}?page_size={DEFAULT_PAGE_SIZE}",),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    @mock.patch("requests.get")
    def test_access_policies_list_by_name(self, mock_get):
        """
        Test access_policy listing
        """
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
                    (
                        (
                            f"url/{ROOT}/{SUBPATH}"
                            f"?page_size={DEFAULT_PAGE_SIZE}"
                            "&display_name=Policy display name"
                        ),
                    ),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    @mock.patch("requests.get")
    def test_access_policies_count_matching_access_policies(self, mock_get):
        """
        Test access_policy counting
        """
        mock_get.return_value = MockResponse(
            200,
            headers={HEADERS_TOTAL_COUNT: 1},
            access_policies=[
                RESPONSE,
            ],
        )

        count = self.arch.access_policies.count_matching_access_policies(ASSET_ID)
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{ASSET_ID}/{ACCESS_POLICIES_LABEL}"
                        "?page_size=1"
                    ),
                ),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: "true",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="GET method called incorrectly",
        )
        self.assertEqual(
            count,
            1,
            msg="Incorrect count",
        )

    @mock.patch("requests.get")
    def test_access_policies_list_matching_access_policies(self, mock_get):
        """
        Test access_policy counting
        """
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
                        f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{ASSET_ID}/{ACCESS_POLICIES_LABEL}"
                        f"?page_size={DEFAULT_PAGE_SIZE}",
                    ),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    @mock.patch("requests.get")
    def test_access_policies_count_matching_assets(self, mock_get):
        """
        Test access_policy counting
        """
        mock_get.return_value = MockResponse(
            200,
            headers={HEADERS_TOTAL_COUNT: 1},
            assets=[
                ASSET,
            ],
        )

        count = self.arch.access_policies.count_matching_assets(IDENTITY)
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{IDENTITY}/{ASSETS_LABEL}"
                        "?page_size=1"
                    ),
                ),
                {
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: "true",
                    },
                    "verify": True,
                    "cert": None,
                },
            ),
            msg="GET method called incorrectly",
        )
        self.assertEqual(
            count,
            1,
            msg="Incorrect count",
        )

    @mock.patch("requests.get")
    def test_access_policies_list_matching_assets(self, mock_get):
        """
        Test access_policy counting
        """
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
                        f"url/{ROOT}/{ACCESS_POLICIES_SUBPATH}/{IDENTITY}/{ASSETS_LABEL}"
                        f"?page_size={DEFAULT_PAGE_SIZE}",
                    ),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )
