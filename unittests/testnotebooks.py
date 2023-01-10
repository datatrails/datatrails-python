"""
Test notebooks
"""
import os
from unittest import TestCase

from testbook import testbook

from archivist.archivist import Archivist

# pylint: disable=missing-function-docstring

# Temporary list that will be deleted eventually when all test are done
LS = """
-rw-rw-r-- 1 paul paul 11004 Dec 20 15:27  Share_Asset.ipynb
"""


URL = "https://app.rkvst-test.io"
AUTHTOKEN = "xxxxxxxxxxxxxxxxxxxx"
APPREG_CLIENT = "yyyyyyyyyyyyyyyyyyyy"
APPREG_SECRET = "zzzzzzzzzzzzzzzzzzzz"
ARTIST_NAME = "Adele Laurie Blue Adkins"
ARTIST_STAGE_NAME = "Adele"
ARTIST_GENRE = "Soul"
ARTIST_ID = "123456789abc"

ARTIST_RESPONSE = {
    "identity": "assets/0c8c04b1-05e1-4653-b438-fd912b0c61b7",
    "behaviours": ["Attachments", "RecordEvidence", "Builtin", "AssetCreator"],
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
    "proof_mechanism": "SIMPLE_HASH",
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


# Commented out code corresponds to
class TestNotebooks(TestCase):
    """
    Test notebooks
    """

    maxDiff = None

    def setUp(self):
        self.archivist = setenv("RKVST_URL", URL)
        self.authtoken = setenv("RKVST_AUTHTOKEN", AUTHTOKEN)
        self.client_id = setenv("RKVST_APPREG_CLIENT", APPREG_CLIENT)
        self.client_secret = setenv("RKVST_APPREG_SECRET", APPREG_SECRET)

    def tearDown(self):
        unsetenv("RKVST_URL", self.archivist)
        unsetenv("RKVST_AUTHTOKEN", self.authtoken)
        unsetenv("RKVST_APPREG_CLIENT", self.client_id)
        unsetenv("RKVST_APPREG_SECRET", self.client_secret)

    def test_manage_credentials(self):
        """
        Test manage_credentials
        """
        with testbook(
            "archivist/notebooks/Manage_Credentials.ipynb", execute=True
        ) as notebook:
            self.assertEqual(
                notebook.ref("URL"),
                os.getenv("RKVST_URL"),
                msg="Incorrect URL",
            )
            self.assertEqual(
                notebook.ref("auth_token"),
                os.getenv("RKVST_AUTHTOKEN"),
                msg="Incorrect AUTHTOKEN",
            )
            self.assertEqual(
                notebook.cell_output_text(5),
                str(Archivist(os.getenv("RKVST_URL"), os.getenv("RKVST_AUTHTOKEN"))),
                msg="Incorrect Archivist",
            )
            self.assertEqual(
                notebook.cell_output_text(6),
                f"""client_id {APPREG_CLIENT}
client_secret {APPREG_SECRET}""",
                msg="Incorrect appreg client id and secret",
            )
            self.assertEqual(
                notebook.cell_output_text(7),
                f"Archivist({URL})",
                msg="Incorrect Archivist",
            )
            self.assertEqual(
                notebook.cell_output_text(8),
                f"Archivist({URL})",
                msg="Incorrect Archivist",
            )

    def basic_notebook_test(self, notebook):
        """
        common test for all notebooks
        """
        self.assertEqual(
            notebook.ref("RKVST_URL"),
            os.getenv("RKVST_URL"),
            msg="Incorrect URL",
        )
        self.assertEqual(
            notebook.ref("APPREG_CLIENT"),
            os.getenv("RKVST_APPREG_CLIENT"),
            msg="Incorrect APPREG_CLIENT",
        )
        self.assertEqual(
            notebook.ref("APPREG_SECRET"),
            os.getenv("RKVST_APPREG_SECRET"),
            msg="Incorrect APPREG_SECRET",
        )
        self.assertEqual(
            notebook.cell_output_text(4),
            f"""Connecting to RKVST
URL {URL}""",
            msg="Incorrect cell output",
        )

    def test_create_asset_and_events(self):
        """
        Test create_asset_and_events
        """
        with testbook(
            "archivist/notebooks/Create Asset and Events.ipynb", execute=range(1, 5)
        ) as notebook:
            self.basic_notebook_test(notebook)

            # this is commenetd out as it does not work. There is no way of patching
            # an object in a notebook (no notebook.patch.object) as notebook code is
            # represented as strings we could 'eval' the strings but for security
            # reasons the __Repr__ of the Archivist does not emit the credentials so
            # this isnot possible.
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
            execute=range(1, 5),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_check_asset_compliance_current_outstanding(self):
        """
        Test check_asset_compliance_current_outstanding
        """
        with testbook(
            "archivist/notebooks/Check Asset Compliance using CURRENT OUTSTANDING Policy.ipynb",
            execute=range(1, 5),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_check_asset_compliance_since(self):
        """
        Test check_asset_compliance_since
        """
        with testbook(
            "archivist/notebooks/Check Asset Compliance using SINCE Policy.ipynb",
            execute=range(1, 5),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_find_asset_create_attachment(self):
        """
        Test find_asset_create_attachment
        """
        with testbook(
            "archivist/notebooks/Find Asset and Create Attachment.ipynb",
            execute=range(1, 5),
        ) as notebook:
            self.basic_notebook_test(notebook)

    def test_find_asset_create_event(self):
        """
        Test find_asste_create_event
        """
        with testbook(
            "archivist/notebooks/Find Asset and Event Creation.ipynb",
            execute=range(1, 5),
        ) as notebook:
            self.basic_notebook_test(notebook)
