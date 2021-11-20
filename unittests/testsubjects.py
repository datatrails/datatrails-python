"""
Test subjects
"""

import json
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    SUBJECTS_SUBPATH,
    SUBJECTS_LABEL,
)
from archivist.errors import ArchivistBadRequestError

from .mock_response import MockResponse


# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

DISPLAY_NAME = "Subject display name"
WALLET_PUB_KEYS = [
    "wallet1",
    "wallet2",
]
WALLET_ADDRESSES = [
    "address1",
    "address2",
]
TESSERA_PUB_KEYS = [
    "tessera1",
    "tessera2",
]
IDENTITY = f"{SUBJECTS_LABEL}/xxxxxxxx"
SUBPATH = f"{SUBJECTS_SUBPATH}/{SUBJECTS_LABEL}"

RESPONSE = {
    "identity": IDENTITY,
    "display_name": DISPLAY_NAME,
    "wallet_pub_key": WALLET_PUB_KEYS,
    "wallet_address": WALLET_ADDRESSES,
    "tessera_pub_key": TESSERA_PUB_KEYS,
}
REQUEST = {
    "display_name": DISPLAY_NAME,
    "wallet_pub_key": WALLET_PUB_KEYS,
    "tessera_pub_key": TESSERA_PUB_KEYS,
}
REQUEST_DATA = json.dumps(REQUEST)
UPDATE_DATA = json.dumps({"display_name": DISPLAY_NAME})


class TestSubjects(TestCase):
    """
    Test Archivist Subjects Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", auth="authauthauth")

    def test_subjects_create(self):
        """
        Test subject creation
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            subject = self.arch.subjects.create(
                DISPLAY_NAME, WALLET_PUB_KEYS, TESSERA_PUB_KEYS
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
                subject,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_subjects_read(self):
        """
        Test subject reading
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            subject = self.arch.subjects.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBJECTS_SUBPATH}/{IDENTITY}"),),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "params": None,
                        "verify": True,
                        "cert": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_subjects_delete(self):
        """
        Test subject deleting
        """
        with mock.patch.object(self.arch._session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(200, {})

            subject = self.arch.subjects.delete(IDENTITY)
            self.assertEqual(
                tuple(mock_delete.call_args),
                (
                    ((f"url/{ROOT}/{SUBJECTS_SUBPATH}/{IDENTITY}"),),
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

    def test_subjects_update(self):
        """
        Test subject deleting
        """
        with mock.patch.object(self.arch._session, "patch") as mock_patch:
            mock_patch.return_value = MockResponse(200, **RESPONSE)

            subject = self.arch.subjects.update(
                IDENTITY,
                display_name=DISPLAY_NAME,
            )
            self.assertEqual(
                tuple(mock_patch.call_args),
                (
                    ((f"url/{ROOT}/{SUBJECTS_SUBPATH}/{IDENTITY}"),),
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

    def test_subjects_read_with_error(self):
        """
        Test read method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(400)
            with self.assertRaises(ArchivistBadRequestError):
                resp = self.arch.subjects.read(IDENTITY)

    def test_subjects_count(self):
        """
        Test subject counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                subjects=[
                    RESPONSE,
                ],
            )

            count = self.arch.subjects.count()
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

    def test_subjects_count_by_name(self):
        """
        Test subject counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                subjects=[
                    RESPONSE,
                ],
            )

            count = self.arch.subjects.count(
                display_name="Subject display name",
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{SUBPATH}"
                            "?page_size=1"
                            "&display_name=Subject display name"
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

    def test_subjects_list(self):
        """
        Test subject listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                subjects=[
                    RESPONSE,
                ],
            )

            subjects = list(self.arch.subjects.list())
            self.assertEqual(
                len(subjects),
                1,
                msg="incorrect number of subjects",
            )
            for subject in subjects:
                self.assertEqual(
                    subject,
                    RESPONSE,
                    msg="Incorrect subject listed",
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
                            "cert": None,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_subjects_list_by_name(self):
        """
        Test subject listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                subjects=[
                    RESPONSE,
                ],
            )

            subjects = list(
                self.arch.subjects.list(
                    display_name="Subject display name",
                )
            )
            self.assertEqual(
                len(subjects),
                1,
                msg="incorrect number of subjects",
            )
            for subject in subjects:
                self.assertEqual(
                    subject,
                    RESPONSE,
                    msg="Incorrect subject listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"url/{ROOT}/{SUBPATH}"
                                "?display_name=Subject display name"
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
