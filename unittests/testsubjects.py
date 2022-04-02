"""
Test subjects
"""

from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    SUBJECTS_SUBPATH,
    SUBJECTS_LABEL,
)
from archivist.errors import ArchivistBadRequestError, ArchivistUnconfirmedError

from .mock_response import MockResponse


# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

DISPLAY_NAME = "Subject display name"
WALLET_PUB_KEYS = [
    (
        "04c1173bf7844bf1c607b79c18db091b9558ffe581bf132b8cf3b37657230fa321a088"
        "0b54a79a88b28bc710ede6dcf3d8272c5210bfd41ea83188e385d12c189c"
    )
]
WALLET_ADDRESSES = ["0xAab979509B595084F5C113c5622Ca9A7844C58B5"]

TESSERA_PUB_KEYS = ["efdg9J0QhSB2g4IxKcaXgJmNKbzpxs03FFYIiYYuekk="]

SUBJECT_STRING = (
    "eyJpZGVudGl0eSI6ICJzdWJqZWN0cy8wMDAwMDAwMC0wMDAwLTAwMDAtMDA"
    "wMC0wMDAwMDAwMDAwMDAiLCAiZGlzcGxheV9uYW1lIjogIlNlbGYiLCAid2"
    "FsbGV0X3B1Yl9rZXkiOiBbIjA0YzExNzNiZjc4NDRiZjFjNjA3Yjc5YzE4Z"
    "GIwOTFiOTU1OGZmZTU4MWJmMTMyYjhjZjNiMzc2NTcyMzBmYTMyMWEwODgw"
    "YjU0YTc5YTg4YjI4YmM3MTBlZGU2ZGNmM2Q4MjcyYzUyMTBiZmQ0MWVhODM"
    "xODhlMzg1ZDEyYzE4OWMiXSwgIndhbGxldF9hZGRyZXNzIjogWyIweDk5Rm"
    "E0QUFCMEFGMkI1M2YxNTgwODNEOGYyNDRiYjQ1MjMzODgxOTciXSwgInRlc"
    "3NlcmFfcHViX2tleSI6IFsiZWZkZzlKMFFoU0IyZzRJeEtjYVhnSm1OS2J6"
    "cHhzMDNGRllJaVlZdWVraz0iXSwgInRlbmFudCI6ICIiLCAiY29uZmlybWF"
    "0aW9uX3N0YXR1cyI6ICJDT05GSVJNQVRJT05fU1RBVFVTX1VOU1BFQ0lGSU"
    "VEIn0="
)

IDENTITY = f"{SUBJECTS_LABEL}/xxxxxxxx"
SUBPATH = f"{SUBJECTS_SUBPATH}/{SUBJECTS_LABEL}"

RESPONSE = {
    "identity": IDENTITY,
    "display_name": DISPLAY_NAME,
    "wallet_pub_key": WALLET_PUB_KEYS,
    "wallet_address": WALLET_ADDRESSES,
    "tessera_pub_key": TESSERA_PUB_KEYS,
}
RESPONSE_WITH_PENDING = {
    **RESPONSE,
    "confirmation_status": "PENDING",
}
RESPONSE_WITH_CONFIRMATION = {
    **RESPONSE,
    "confirmation_status": "CONFIRMED",
}
REQUEST = {
    "display_name": DISPLAY_NAME,
    "wallet_pub_key": WALLET_PUB_KEYS,
    "tessera_pub_key": TESSERA_PUB_KEYS,
}
UPDATE = {"display_name": DISPLAY_NAME}


class TestSubjects(TestCase):
    """
    Test Archivist Subjects Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=1)

    def test_subjects_str(self):
        """
        Test subjecty str
        """
        self.assertEqual(
            str(self.arch.subjects),
            "SubjectsClient(url)",
            msg="Incorrect str",
        )

    def test_subjects_create(self):
        """
        Test subject creation
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            subject = self.arch.subjects.create(
                DISPLAY_NAME, WALLET_PUB_KEYS, TESSERA_PUB_KEYS
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
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                subject,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_subjects_create_from_b64(self):
        """
        Test subject creation
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            subject = self.arch.subjects.create_from_b64(
                {
                    "display_name": DISPLAY_NAME,
                    "subject_string": SUBJECT_STRING,
                }
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
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                subject,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_subjects_create_with_confirmation(self):
        """
        Test subjects creation
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            subject = self.arch.subjects.create(
                DISPLAY_NAME, WALLET_PUB_KEYS, TESSERA_PUB_KEYS
            )
            self.assertEqual(
                subject,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )
            with mock.patch.object(self.arch._session, "get") as mock_get:
                mock_get.side_effect = [
                    MockResponse(200, **RESPONSE),
                    MockResponse(200, **RESPONSE_WITH_PENDING),
                    MockResponse(200, **RESPONSE_WITH_CONFIRMATION),
                ]
                self.assertEqual(
                    self.arch.subjects.wait_for_confirmation(subject["identity"]),
                    RESPONSE_WITH_CONFIRMATION,
                    msg="wait_for_confirmation called incorrectly",
                )

    def test_subjects_create_with_confirmation_unconfirmed(self):
        """
        Test subjects creation
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            subject = self.arch.subjects.create(
                DISPLAY_NAME, WALLET_PUB_KEYS, TESSERA_PUB_KEYS
            )
            self.assertEqual(
                subject,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )
            with mock.patch.object(self.arch._session, "get") as mock_get:
                mock_get.side_effect = [
                    MockResponse(200, **RESPONSE),
                    MockResponse(200, **RESPONSE_WITH_PENDING),
                    MockResponse(200, **RESPONSE_WITH_PENDING),
                    MockResponse(200, **RESPONSE_WITH_PENDING),
                    MockResponse(200, **RESPONSE_WITH_PENDING),
                    MockResponse(200, **RESPONSE_WITH_PENDING),
                ]
                with self.assertRaises(ArchivistUnconfirmedError):
                    self.arch.subjects.wait_for_confirmation(subject["identity"])

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
                            "authorization": "Bearer authauthauth",
                        },
                        "params": None,
                        "verify": True,
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
                            "authorization": "Bearer authauthauth",
                        },
                        "verify": True,
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
            args, kwargs = mock_patch.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBJECTS_SUBPATH}/{IDENTITY}",),
                msg="PATCH method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": UPDATE,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="PATCH method kwargs called incorrectly",
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
                    ((f"url/{ROOT}/{SUBPATH}"),),
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
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {
                            "page_size": 1,
                            "display_name": "Subject display name",
                        },
                        "verify": True,
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
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {},
                            "verify": True,
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
                        ((f"url/{ROOT}/{SUBPATH}"),),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {"display_name": "Subject display name"},
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )
