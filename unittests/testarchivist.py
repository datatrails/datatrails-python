"""
Test archivist
"""

from copy import copy
from os import environ
from unittest import TestCase, mock

from archivist.about import __version__ as VERSION
from archivist.archivist import Archivist
from archivist.constants import (
    HEADERS_RETRY_AFTER,
    HEADERS_TOTAL_COUNT,
    USER_AGENT,
    USER_AGENT_PREFIX,
)
from archivist.errors import (
    ArchivistBadRequestError,
    ArchivistError,
    ArchivistHeaderError,
    ArchivistTooManyRequestsError,
)
from archivist.logger import set_logger

from .mock_response import MockResponse

# pylint: disable=unused-variable
# pylint: disable=missing-docstring
# pylint: disable=protected-access

if "DATATRAILS_LOGLEVEL" in environ and environ["DATATRAILS_LOGLEVEL"]:
    set_logger(environ["DATATRAILS_LOGLEVEL"])


DATATRAILS_APPREG_CLIENT = "client_id-2f78-4fa0-9425-d59314845bc5"
DATATRAILS_APPREG_SECRET = "client_secret-388f5187e32d930d83"
ACCESS_TOKEN = "access_token-xbXATAWrEpepR7TklOxRB-yud92AsD6DGGasiEGN7MZKT0AIQ4Rw9s"
REQUEST = {
    "grant_type": "client_credentials",
    "client_id": DATATRAILS_APPREG_CLIENT,
    "client_secret": DATATRAILS_APPREG_SECRET,
}

RESPONSE = {
    "access_token": ACCESS_TOKEN,
    "expires_in": 660,
    "token_type": "Bearer",
}
NONE_RESPONSE = {
    "access_token": None,
    "expires_in": 660,
    "token_type": "Bearer",
}


class TestArchivist(TestCase):
    """
    Test Archivist class
    """

    def test_archivist_illegal_url(self):
        """
        Test illegal url
        """
        with self.assertRaises(ArchivistError):
            Archivist("https://app.datatrails.ai/", "authauthauth")

    def test_archivist(self):
        """
        Test default archivist creation
        """
        with Archivist("https://app.datatrails.ai", "authauthauth") as arch:
            self.assertEqual(
                str(arch),
                "Archivist(https://app.datatrails.ai)",
                msg="Incorrect str",
            )
            self.assertEqual(
                str(arch.access_policies),
                "AccessPoliciesClient(https://app.datatrails.ai)",
                msg="Incorrect access_policies",
            )
            self.assertEqual(
                str(arch.appidp),
                "AppIDPClient(https://app.datatrails.ai)",
                msg="Incorrect appidp",
            )
            self.assertEqual(
                str(arch.applications),
                "ApplicationsClient(https://app.datatrails.ai)",
                msg="Incorrect applications",
            )
            self.assertEqual(
                str(arch.assets),
                "AssetsRestricted(https://app.datatrails.ai)",
                msg="Incorrect assets",
            )
            self.assertEqual(
                str(arch.assetattachments),
                "AssetAttachmentsClient(https://app.datatrails.ai)",
                msg="Incorrect assets",
            )
            self.assertEqual(
                str(arch.attachments),
                "AttachmentsClient(https://app.datatrails.ai)",
                msg="Incorrect attachments",
            )
            self.assertEqual(
                str(arch.events),
                "EventsRestricted(https://app.datatrails.ai)",
                msg="Incorrect events",
            )
            self.assertEqual(
                str(arch.locations),
                "LocationsClient(https://app.datatrails.ai)",
                msg="Incorrect locations",
            )
            self.assertEqual(
                str(arch.runner),
                "Runner(https://app.datatrails.ai)",
                msg="Incorrect runner",
            )
            self.assertEqual(
                str(arch.subjects),
                "SubjectsClient(https://app.datatrails.ai)",
                msg="Incorrect subjects",
            )
            self.assertEqual(
                str(arch.Public),
                "ArchivistPublic()",
                msg="Incorrect Public",
            )
            self.assertEqual(
                arch.url,
                "https://app.datatrails.ai",
                msg="Incorrect url",
            )
            self.assertEqual(
                arch.auth,
                "authauthauth",
                msg="Incorrect auth",
            )
            self.assertEqual(
                arch.root,
                "https://app.datatrails.ai/archivist",
                msg="Incorrect root",
            )
            self.assertEqual(
                arch.verify,
                True,
                msg="verify must be True",
            )
            with self.assertRaises(AttributeError):
                arch.Illegal_endpoint

    def test_archivist_token(self):
        """
        Test archivist creation with app registration
        """
        with (
            Archivist(
                "https://app.datatrails.ai",
                (DATATRAILS_APPREG_CLIENT, DATATRAILS_APPREG_SECRET),
            ) as arch,
            mock.patch.object(arch.appidp, "token") as mock_token,
        ):
            mock_token.return_value = RESPONSE
            self.assertEqual(
                arch.auth,
                ACCESS_TOKEN,
                msg="Incorrect auth",
            )

    def test_archivist_none_token(self):
        """
        Test archivist creation with no token
        """
        with Archivist("https://app.datatrails.ai", None) as arch:
            self.assertIsNone(
                arch.auth,
                msg="Incorrect auth",
            )

    def test_archivist_appidp_token(self):
        """
        Test archivist creation with appidp token
        """
        with (
            Archivist(
                "https://app.datatrails.ai",
                (DATATRAILS_APPREG_CLIENT, DATATRAILS_APPREG_SECRET),
            ) as arch,
            mock.patch.object(arch.appidp, "token") as mock_token,
        ):
            mock_token.return_value = NONE_RESPONSE
            with self.assertRaises(ArchivistError):
                _ = arch.auth

    def test_archivist_copy(self):
        """
        Test archivist copy
        """
        with Archivist(
            "https://app.datatrails.ai", "authauthauth", verify=False
        ) as arch:
            arch1 = copy(arch)
            self.assertEqual(
                arch.url,
                arch1.url,
                msg="Incorrect url",
            )
            self.assertEqual(
                arch.verify,
                arch1.verify,
                msg="Incorrect verify",
            )
            self.assertEqual(
                arch.fixtures,
                arch1.fixtures,
                msg="Incorrect fixtures",
            )

    def test_archivist_no_verify(self):
        """
        Test archivist creation with no verify
        """
        with Archivist(
            "https://app.datatrails.ai", "authauthauth", verify=False
        ) as arch:
            self.assertFalse(
                arch.verify,
                msg="verify must be False",
            )


class TestArchivistMethods(TestCase):
    """
    Test Archivist base method class
    """

    def setUp(self):
        self.arch = Archivist("https://app.datatrails.ai", "authauthauth")

    def tearDown(self):
        self.arch.close()


class TestArchivistPatch(TestArchivistMethods):
    """
    Test Archivist PATCH method
    """

    def test_patch(self):
        """
        Test default patch method
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(200, request=request)
            self.arch.patch("path/path/entity/xxxx", request)
            args, kwargs = mock_patch.call_args
            self.assertEqual(
                args,
                ("path/path/entity/xxxx",),
                msg="POST method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": request,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="POST method kwargs called incorrectly",
            )

    def test_patch_with_error(self):
        """
        Test post method with error
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(
                400, request=request, field1="value1"
            )
            with self.assertRaises(ArchivistBadRequestError):
                self.arch.patch("path/path/entity/xxxx", request)

    def test_patch_with_headers(self):
        """
        Test default patch method
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(200, request=request)
            self.arch.patch(
                "path/path/entity/xxxx",
                request,
                headers={
                    "headerfield1": "headervalue1",
                    USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                },
            )
            args, kwargs = mock_patch.call_args
            self.assertEqual(
                args,
                ("path/path/entity/xxxx",),
                msg="PATCH method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": request,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                        "headerfield1": "headervalue1",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="PATCH method kwargs called incorrectly",
            )

    def test_patch_with_429(self):
        """
        Test patch method with error
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(429, request=request)
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.patch(
                    "path/path/id/xxxxxxxx",
                    request,
                )

    def test_patch_with_429_retry_and_fail(self):
        """
        Test patch method with 429 retry and fail
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "patch") as mock_patch:
            mock_patch.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, request=request),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.patch(
                    "path/path/id/xxxxxxxx",
                    request,
                )

    def test_patch_with_429_retry_and_retries_fail(self):
        """
        Test patch method with 429 retry and retries_fail
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "patch") as mock_patch:
            mock_patch.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.patch(
                    "path/path/id/xxxxxxxx",
                    request,
                )

    def test_patch_with_429_retry_and_success(self):
        """
        Test patch method with 429 retry and success
        """
        request = {"field1": "value1"}
        with mock.patch.object(self.arch.session, "patch") as mock_patch:
            mock_patch.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}, request=request),
                MockResponse(200, request=request),
            )
            self.arch.patch("path/path/entity/xxxxxxxx", request)
            args, kwargs = mock_patch.call_args
            self.assertEqual(
                args,
                ("path/path/entity/xxxxxxxx",),
                msg="PATCH method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": request,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="PATCH method kwargs called incorrectly",
            )


class TestArchivistCount(TestArchivistMethods):
    """
    Test Archivist count method
    """

    def test_count(self):
        """
        Test default count method
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT.lower(): 1},
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            count = self.arch.count("path/path")
            self.assertEqual(
                count,
                1,
                msg="incorrect count",
            )

    def test_count_with_error(self):
        """
        Test default count method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                400,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistBadRequestError):
                self.arch.count("path/path")

    def test_count_with_missing_count_error(self):
        """
        Tests the default count method raises a ArchivistHeaderError when the
        expected count header field is missing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                things=[
                    {
                        "field1": "value1",
                    },
                ],
            )
            with self.assertRaises(ArchivistHeaderError):
                self.arch.count("path/path")

    def test_count_with_429(self):
        """
        Test count method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(429)
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.count("path/path")

    def test_count_with_429_retry_and_fail(self):
        """
        Test count method with 429 retry and fail
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.count("path/path")

    def test_count_with_429_retry_and_retries_fail(self):
        """
        Test count method with 429 retry and retries_fail
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
            )
            with self.assertRaises(ArchivistTooManyRequestsError):
                self.arch.count("path/path")

    def test_count_with_429_retry_and_success(self):
        """
        Test count method with 429 retry and success
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.side_effect = (
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(429, headers={HEADERS_RETRY_AFTER: 0.1}),
                MockResponse(
                    200,
                    headers={HEADERS_TOTAL_COUNT: 1},
                    things=[
                        {
                            "field1": "value1",
                        },
                    ],
                ),
            )
            count = self.arch.count("path/path")
            self.assertEqual(
                count,
                1,
                msg="incorrect count",
            )
