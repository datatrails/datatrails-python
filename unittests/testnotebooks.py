"""
Test notebooks
"""

import os
from sys import version_info
from unittest import TestCase, skipIf

from testbook import testbook

from archivist.archivist import Archivist

# pylint: disable=missing-function-docstring

# Temporary list that will be deleted eventually when all test are done
LS = """
-rw-rw-r-- 1 paul paul 11004 Dec 20 15:27  Share_Asset.ipynb
"""


URL = "https://app.datatrails-test.io"
AUTHTOKEN = "xxxxxxxxxxxxxxxxxxxx"
APPREG_CLIENT = "yyyyyyyyyyyyyyyyyyyy"
APPREG_SECRET = "zzzzzzzzzzzzzzzzzzzz"
ARTIST_NAME = "Adele Laurie Blue Adkins"
ARTIST_STAGE_NAME = "Adele"
ARTIST_GENRE = "Soul"
ARTIST_ID = "123456789abc"

ARTIST_RESPONSE = {
    "identity": "assets/0c8c04b1-05e1-4653-b438-fd912b0c61b7",
    "behaviours": ["RecordEvidence", "Builtin", "AssetCreator"],
    "attributes": {
        "arc_description": "British Soul Singer",
        "arc_display_name": ARTIST_NAME,
        "arc_display_type": "Artists",
        "artistid": ARTIST_ID,
        "genre": ARTIST_GENRE,
        "stage_name": ARTIST_STAGE_NAME,
    },
    "confirmation_status": "CONFIRMED",
    "tracked": "TRACKED",
    "owner": "0x5284e740A744F075E402f7fB0c4485532ddf4Af8",
    "at_time": "2023-01-06T17:41:26Z",
    "storage_integrity": "TENANT_STORAGE",
    "chain_id": "8275868384",
    "public": False,
    "tenant_identity": "tenant/0a62f7c9-fd7b-4791-8041-01218d839ec1",
}


def setenv(key, newvalue):
    val = os.getenv(key)
    os.environ[key] = newvalue
    return val


def unsetenv(key, oldvalue):
    if oldvalue is not None:
        os.environ[key] = oldvalue
    else:
        del os.environ[key]


@skipIf(
    version_info >= (3, 12),
    "cannot run test as notebooks unsupported in 3.12",
)
class TestNotebooks(TestCase):
    """
    Test notebooks
    """

    maxDiff = None

    def setUp(self):
        self.archivist = setenv("DATATRAILS_URL", URL)
        self.authtoken = setenv("DATATRAILS_AUTHTOKEN", AUTHTOKEN)
        self.client_id = setenv("DATATRAILS_APPREG_CLIENT", APPREG_CLIENT)
        self.client_secret = setenv("DATATRAILS_APPREG_SECRET", APPREG_SECRET)

    def tearDown(self):
        unsetenv("DATATRAILS_URL", self.archivist)
        unsetenv("DATATRAILS_AUTHTOKEN", self.authtoken)
        unsetenv("DATATRAILS_APPREG_CLIENT", self.client_id)
        unsetenv("DATATRAILS_APPREG_SECRET", self.client_secret)

    def test_manage_credentials(self):
        """
        Test manage_credentials
        """
        with testbook(
            "archivist/notebooks/Manage_Credentials.ipynb", execute=True
        ) as notebook:
            self.assertEqual(
                notebook.ref("DATATRAILS_URL"),
                f"{URL}",
                msg="Incorrect URL",
            )
            self.assertEqual(
                notebook.ref("auth_token"),
                f"{AUTHTOKEN}",
                msg="Incorrect AUTHTOKEN",
            )
            self.assertEqual(
                notebook.cell_output_text(6),
                str(Archivist(f"{URL}", f"{AUTHTOKEN}")),
                msg="Incorrect Archivist",
            )
            self.assertEqual(
                notebook.cell_output_text(7),
                f"""DATATRAILS_APPREG_CLIENT {APPREG_CLIENT}
DATATRAILS_APPREG_SECRET {APPREG_SECRET}""",
                msg="Incorrect appreg client id and secret",
            )
            self.assertEqual(
                notebook.cell_output_text(8),
                f"Archivist({URL})",
                msg="Incorrect Archivist",
            )
            self.assertEqual(
                notebook.cell_output_text(9),
                f"Archivist({URL})",
                msg="Incorrect Archivist",
            )

    def basic_notebook_test(self, notebook):
        """
        common test for all notebooks
        """
        self.assertEqual(
            notebook.ref("DATATRAILS_URL"),
            f"{URL}",
            msg="Incorrect URL",
        )
        self.assertEqual(
            notebook.ref("DATATRAILS_APPREG_CLIENT"),
            f"{APPREG_CLIENT}",
            msg="Incorrect APPREG_CLIENT",
        )
        self.assertEqual(
            notebook.ref("DATATRAILS_APPREG_SECRET"),
            f"{APPREG_SECRET}",
            msg="Incorrect APPREG_SECRET",
        )
        self.assertEqual(
            notebook.cell_output_text(5),
            f"""Connecting to DATATRAILS
DATATRAILS_URL {URL}""",
            msg="Incorrect cell output",
        )

    def test_create_artist_albuminfo(self):
        """
        Test create_artist_albuminfo
        """
        with testbook(
            "archivist/notebooks/Create Artist and Album Release Info.ipynb",
            execute=(1, 2, 4, 5),
        ) as notebook:
            self.basic_notebook_test(notebook)

            # this is commented out as it does not work. There is no way of patching
            # an object in a notebook (no notebook.patch.object) as notebook code is
            # represented as strings we could 'eval' the strings but for security
            # reasons the __repr__ of the Archivist does not emit the credentials so
            # this is not possible.
            # so we will implement functional tests to test actual code
            # arch = notebook.ref("arch")
            # create_artist = notebook.ref("create_artist")
            # with mock.patch.object(arch.session, "post", autospec=True) as mock_post:
            #    mock_post.return_value = MockResponse(200, **ARTIST_RESPONSE)
            #    artist = create_artist(
            #        arch, ARTIST_NAME, ARTIST_STAGE_NAME, ARTIST_GENRE, ARTIST_ID
            #    )
            #    print("artist", artist)

    def test_create_event_with_verified_domain(self):
        """
        Test create_event_with_verified_domain
        """
        with testbook(
            "archivist/notebooks/Create Event with Verified Domain.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_check_asset_compliance_current_outstanding(self):
        """
        Test check_asset_compliance_current_outstanding
        """
        with testbook(
            "archivist/notebooks/Check Asset Compliance using CURRENT OUTSTANDING Policy.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_check_asset_compliance_since(self):
        """
        Test check_asset_compliance_since
        """
        with testbook(
            "archivist/notebooks/Check Asset Compliance using SINCE Policy.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_find_artist_cover_art(self):
        """
        Test find_artist_cover_art
        """
        with testbook(
            "archivist/notebooks/Find Artist and Create Cover Art.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_find_asset_addtl_albuminfo(self):
        """
        Test find_asset_addtl_albuminfo
        """
        with testbook(
            "archivist/notebooks/Find Artist and Additional Album Release Info.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_playing_fetch_fiveminutes(self):
        """
        Test playing_fetch_fiveminutes
        """
        with testbook(
            "archivist/notebooks/Playing Fetch Every 5 Minutes.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_feed_the_dog(self):
        """
        Test feed_the_dog
        """
        with testbook(
            "archivist/notebooks/Feeding the Dog.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_feed_the_doghourly(self):
        """
        Test feed_the_doghourly
        """
        with testbook(
            "archivist/notebooks/Feeding the Dog Hourly.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_checking_dogs_weight(self):
        """
        Test checking_dogs_weight
        """
        with testbook(
            "archivist/notebooks/Checking the Dog's Weight.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_feed_dog_timelymanner(self):
        """
        Test feed_dog_timelymanner
        """
        with testbook(
            "archivist/notebooks/Feeding the Dog in a Timely Manner.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_share_artist_asset_user(self):
        """
        Test share_artist_asset_user
        """
        with testbook(
            "archivist/notebooks/Sharing Artist Asset with User.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_share_album_release_user(self):
        """
        Test share_album_release_user
        """
        with testbook(
            "archivist/notebooks/Sharing Album Release Info with User.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_share_artist_asset_recordlabel(self):
        """
        Test share_artist_asset_recordlabel
        """
        with testbook(
            "archivist/notebooks/Sharing Artist Asset with Record Labels.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_share_album_release_recordlabel(self):
        """
        Test share_album_release_recordlabel
        """
        with testbook(
            "archivist/notebooks/Sharing Album Release Info with Record Labels.ipynb",
            execute=range(1, 6),
        ) as notebook:
            self.basic_notebook_test(notebook)
