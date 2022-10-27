"""
Test subjects
"""
from json import dumps as json_dumps
from os import getenv
from unittest import TestCase
from uuid import uuid4

from archivist.archivist import Archivist
from archivist.utils import get_auth

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable

from archivist import logger

if getenv("TEST_DEBUG") is not None:
    logger.set_logger(getenv("TEST_DEBUG"))
else:
    logger.set_logger("INFO")

LOGGER = logger.LOGGER

DISPLAY_NAME = "Subject display name"
WALLET_PUB_KEY = [
    (
        "04c1173bf7844bf1c607b79c18db091b9558ffe581bf132b8cf3b37657230fa321a088"
        "0b54a79a88b28bc710ede6dcf3d8272c5210bfd41ea83188e385d12c189c"
    )
]
WALLET_ADDRESSES = ["0xAab979509B595084F5C113c5622Ca9A7844C58B5"]

TESSERA_PUB_KEY = ["efdg9J0QhSB2g4IxKcaXgJmNKbzpxs03FFYIiYYuekk="]

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


class TestSubjects(TestCase):
    """
    Test Archivist Subjects Create method
    """

    maxDiff = None

    def setUp(self):
        auth = get_auth(
            auth_token_filename=getenv("TEST_AUTHTOKEN_FILENAME"),
            client_id=getenv("TEST_CLIENT_ID"),
            client_secret=getenv("TEST_CLIENT_SECRET"),
            client_secret_filename=getenv("TEST_CLIENT_SECRET_FILENAME"),
        )
        self.arch = Archivist(getenv("TEST_ARCHIVIST"), auth, verify=False)
        self.display_name = f"{DISPLAY_NAME} {uuid4()}"

    def tearDown(self):
        self.arch.close()

    def test_subjects_create(self):
        """
        Test subject creation
        """
        subject = self.arch.subjects.create(
            self.display_name, WALLET_PUB_KEY, TESSERA_PUB_KEY
        )
        self.assertEqual(
            subject["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )

    def test_subjects_create_b64(self):
        """
        Test subject creation
        """
        subject = self.arch.subjects.create_from_b64(
            {
                "display_name": self.display_name,
                "subject_string": SUBJECT_STRING,
            }
        )
        print("subject:", json_dumps(subject, indent=4))
        self.assertEqual(
            subject["display_name"],
            self.display_name,
            msg="Incorrect display_name",
        )
        self.assertEqual(
            subject["wallet_pub_key"],
            WALLET_PUB_KEY,
            msg="Incorrect wallet_pub_key",
        )
        self.assertEqual(
            subject["tessera_pub_key"],
            TESSERA_PUB_KEY,
            msg="Incorrect tessera_pub_key",
        )

    def test_subjects_update(self):
        """
        Test subject update
        """
        subject = self.arch.subjects.create(
            self.display_name, WALLET_PUB_KEY, TESSERA_PUB_KEY
        )
        self.assertEqual(
            subject["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        subject = self.arch.subjects.update(
            subject["identity"],
            display_name=self.display_name,
            wallet_pub_key=WALLET_PUB_KEY,
            tessera_pub_key=TESSERA_PUB_KEY,
        )

    def test_subjects_delete(self):
        """
        Test subject delete
        """
        subject = self.arch.subjects.create(
            self.display_name, WALLET_PUB_KEY, TESSERA_PUB_KEY
        )
        self.assertEqual(
            subject["display_name"],
            self.display_name,
            msg="Incorrect display name",
        )
        subject = self.arch.subjects.delete(
            subject["identity"],
        )
        self.assertEqual(
            subject,
            {},
            msg="Incorrect subject",
        )

    def test_subjects_list(self):
        """
        Test subject list
        """
        subjects = list(self.arch.subjects.list())
        for i, subject in enumerate(subjects):
            print(i, ":", json_dumps(subject, indent=4))

        for subject in subjects:
            self.assertGreater(
                len(subject["display_name"]),
                0,
                msg="Incorrect display name",
            )

    def test_subjects_count(self):
        """
        Test subject count
        """
        count = self.arch.subjects.count()
        self.assertIsInstance(
            count,
            int,
            msg="Count did not return an integer",
        )
