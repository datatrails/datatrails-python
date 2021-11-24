"""
Test applications
"""

import json
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    APPLICATIONS_SUBPATH,
    APPLICATIONS_LABEL,
    APPLICATIONS_REGENERATE,
)
from archivist.errors import ArchivistBadRequestError

from .mock_response import MockResponse


# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

DISPLAY_NAME = "Application display name"
CUSTOM_CLAIMS = {
    "serial_number": "TL1000000101",
    "has_cyclist_light": "true",
}
IDENTITY = f"{APPLICATIONS_LABEL}/xxxxxxxx"
SUBPATH = f"{APPLICATIONS_SUBPATH}/{APPLICATIONS_LABEL}"

RESPONSE = {
    "identity": IDENTITY,
    "display_name": DISPLAY_NAME,
    "custom_claims": CUSTOM_CLAIMS,
    "client_id": "d1fb6c87-faa9-4d56-b2fd-a5b70a9af065",
    "tenant_id": "tenant/53e6bed7-6f4c-4a37-8c4f-cf889f2b1aa6",
    "credentials": [
        {
            "secret": "a0c09972b6ac912a4d67815fef88093c81a99b49977d35ecf6d162631aa29173",
            "valid_from": "2021-09-21T16:43:19Z",
            "valid_until": "2022-09-21T16:43:19Z",
        }
    ],
}
REQUEST = {
    "display_name": DISPLAY_NAME,
    "custom_claims": CUSTOM_CLAIMS,
}
REQUEST_DATA = json.dumps(REQUEST)
UPDATE_DATA = json.dumps({"display_name": DISPLAY_NAME})


class TestApplications(TestCase):
    """
    Test Archivist Applications Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def test_applications_create(self):
        """
        Test application creation
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            application = self.arch.applications.create(
                DISPLAY_NAME,
                CUSTOM_CLAIMS,
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
                    },
                ),
                msg="CREATE method called incorrectly",
            )
            self.assertEqual(
                application,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_applications_read(self):
        """
        Test application reading
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            application = self.arch.applications.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{APPLICATIONS_SUBPATH}/{IDENTITY}"),),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "params": None,
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_applications_delete(self):
        """
        Test application deleting
        """
        with mock.patch.object(self.arch._session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(200, {})

            application = self.arch.applications.delete(IDENTITY)
            self.assertEqual(
                tuple(mock_delete.call_args),
                (
                    ((f"url/{ROOT}/{APPLICATIONS_SUBPATH}/{IDENTITY}"),),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                    },
                ),
                msg="DELETE method called incorrectly",
            )

    def test_applications_update(self):
        """
        Test application deleting
        """
        with mock.patch.object(self.arch._session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(200, **RESPONSE)

            application = self.arch.applications.update(
                IDENTITY,
                display_name=DISPLAY_NAME,
            )
            self.assertEqual(
                tuple(mock_patch.call_args),
                (
                    ((f"url/{ROOT}/{APPLICATIONS_SUBPATH}/{IDENTITY}"),),
                    {
                        "data": UPDATE_DATA,
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
                    },
                ),
                msg="PATCH method called incorrectly",
            )

    def test_applications_read_with_error(self):
        """
        Test read method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(400)
            with self.assertRaises(ArchivistBadRequestError):
                resp = self.arch.applications.read(IDENTITY)

    def test_applications_list(self):
        """
        Test application listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                applications=[
                    RESPONSE,
                ],
            )

            applications = list(self.arch.applications.list())
            self.assertEqual(
                len(applications),
                1,
                msg="incorrect number of applications",
            )
            for application in applications:
                self.assertEqual(
                    application,
                    RESPONSE,
                    msg="Incorrect application listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/{SUBPATH}",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_applications_list_by_name(self):
        """
        Test application listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                applications=[
                    RESPONSE,
                ],
            )

            applications = list(
                self.arch.applications.list(
                    display_name="Application display name",
                )
            )
            self.assertEqual(
                len(applications),
                1,
                msg="incorrect number of applications",
            )
            for application in applications:
                self.assertEqual(
                    application,
                    RESPONSE,
                    msg="Incorrect application listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"url/{ROOT}/{SUBPATH}"
                                "?display_name=Application display name"
                            ),
                        ),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_applications_regenerate(self):
        """
        Test Application regenerate
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            sbom = self.arch.applications.regenerate(IDENTITY)
            self.assertEqual(
                tuple(mock_post.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{APPLICATIONS_SUBPATH}/{IDENTITY}"
                            f":{APPLICATIONS_REGENERATE}"
                        ),
                    ),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "data": None,
                        "verify": True,
                    },
                ),
                msg="POST method called incorrectly",
            )
