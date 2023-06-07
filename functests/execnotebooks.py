"""
Test subjects
"""
from os import getenv
from unittest import skip

from testbook import testbook

# pylint: disable=fixme
# pylint: disable=missing-docstring
# pylint: disable=unused-variable
from archivist import logger
from archivist.archivist import Archivist

from .constants import TestCase

if getenv("RKVST_LOGLEVEL") is not None:
    logger.set_logger(getenv("RKVST_LOGLEVEL"))

LOGGER = logger.LOGGER


class TestNotebooks(TestCase):
    """
    Test Archivist Notebooks
    """

    maxDiff = None

    def setUp(self):
        self.client_id = getenv("RKVST_APPREG_CLIENT")
        self.client_secret = getenv("RKVST_APPREG_SECRET")
        self.url = getenv("RKVST_URL")
        self.arch = Archivist(self.url, (self.client_id, self.client_secret))

    def tearDown(self):
        self.arch.close()

    def basic_notebook_test(self, notebook):
        """
        common test for all notebooks
        """
        self.assertEqual(
            notebook.ref("RKVST_URL"),
            self.url,
            msg="Incorrect URL",
        )
        self.assertEqual(
            notebook.ref("RKVST_APPREG_CLIENT"),
            self.client_id,
            msg="Incorrect RKVST_APPREG_CLIENT",
        )
        self.assertEqual(
            notebook.ref("RKVST_APPREG_SECRET"),
            self.client_secret,
            msg="Incorrect RKVST_APPREG_SECRET",
        )
        self.assertEqual(
            notebook.cell_output_text(5),
            f"""Connecting to RKVST
RKVST_URL {self.url}""",
            msg="Incorrect cell output",
        )

    def check_notebook_cell(self, notebook, cellno):
        """
        Check cell output
        """
        out = notebook.cell_output_text(cellno)
        self.assertNotRegex(
            out,
            r"Archivist*Error",
            msg="Incorrect cell output",
        )
        LOGGER.debug(out)

    def test_01_create_artist_albuminfo(self):
        """
        Test create_artist_albuminfo
        """
        with testbook(
            "archivist/notebooks/Create Artist and Album Release Info.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\ncreate_artist_albuminfo")
            self.basic_notebook_test(notebook)
            self.assertGreater(
                int(notebook.ref("RKVST_UNIQUE_ID")),
                0,
                msg="Incorrect RKVST_UNIQUE_ID",
            )
            self.check_notebook_cell(notebook, 8)
            self.check_notebook_cell(notebook, 9)
            LOGGER.debug("=================================")

    def test_02_find_artist_create_coverart(self):
        """
        Test find_artist_create_coverart
        """
        with testbook(
            "archivist/notebooks/Find Artist and Create Cover Art.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\nfind_artist_create_coverart")
            self.basic_notebook_test(notebook)
            self.assertGreater(
                int(notebook.ref("RKVST_UNIQUE_ID")),
                0,
                msg="Incorrect RKVST_UNIQUE_ID",
            )
            self.assertGreater(
                len(notebook.ref("RKVST_ARTIST_ATTACHMENT")),
                0,
                msg="Incorrect RKVST_ARTIST_ATTACHMENT",
            )
            self.check_notebook_cell(notebook, 9)
            self.check_notebook_cell(notebook, 10)
            LOGGER.debug("=================================")

    def test_03_find_artist_addtl_albuminfo(self):
        """
        Test find_artist_addtl_albuminfo
        """
        with testbook(
            "archivist/notebooks/Find Artist and Additional Album Release Info.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\nfind_asset_addtl_albuminfo")
            self.basic_notebook_test(notebook)
            self.assertGreater(
                int(notebook.ref("RKVST_UNIQUE_ID")),
                0,
                msg="Incorrect RKVST_UNIQUE_ID",
            )
            self.check_notebook_cell(notebook, 8)
            self.check_notebook_cell(notebook, 9)
            LOGGER.debug("=================================")

    def test_create_event_with_verified_domain(self):
        """
        Test create_event_with_verified_domain
        """
        with testbook(
            "archivist/notebooks/Create Event with Verified Domain.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\ncreate_event_with_verified_domain")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 9)
            self.check_notebook_cell(notebook, 10)
            self.check_notebook_cell(notebook, 11)
            LOGGER.debug("=================================")

    def test_check_asset_compliance_current_outstanding(self):
        """
        Test check_asset_compliance_current_outstanding
        """
        with testbook(
            "archivist/notebooks/Check Asset Compliance using CURRENT OUTSTANDING Policy.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\ncheck_asset_compliance_current_outstanding")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 10)
            self.check_notebook_cell(notebook, 11)
            self.check_notebook_cell(notebook, 12)
            self.check_notebook_cell(notebook, 13)
            self.check_notebook_cell(notebook, 14)
            self.check_notebook_cell(notebook, 15)
            self.check_notebook_cell(notebook, 16)
            LOGGER.debug("=================================")

    def test_check_asset_compliance_since(self):
        """
        Test check_asset_compliance_since
        """
        with testbook(
            "archivist/notebooks/Check Asset Compliance using SINCE Policy.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\ncheck_asset_compliance_since")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 10)
            self.check_notebook_cell(notebook, 11)
            self.check_notebook_cell(notebook, 12)
            self.check_notebook_cell(notebook, 13)
            LOGGER.debug("=================================")

    def test_create_compliance_since(self):
        """
        Test create_compliance_since
        """
        with testbook(
            "archivist/notebooks/Create Compliance SINCE Policy.ipynb", execute=True
        ) as notebook:
            LOGGER.debug("\ncreate_compliance_since")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 7)
            LOGGER.debug("=================================")

    def test_create_compliance_current_outstanding(self):
        """
        Test create_compliance_current_outstanding
        """
        with testbook(
            "archivist/notebooks/Create Compliance CURRENT OUTSTANDING Policy.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\ncreate_compliance_current_outstanding")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 7)
            LOGGER.debug("=================================")

    def test_create_compliance_period_outstanding(self):
        """
        Test create_compliance_period_outstanding
        """
        with testbook(
            "archivist/notebooks/Create Compliance PERIOD OUTSTANDING Policy.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\ncreate_compliance_period_outstanding")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 7)
            LOGGER.debug("=================================")

    def test_create_compliance_richness(self):
        """
        Test create_compliance_richness
        """
        with testbook(
            "archivist/notebooks/Create Compliance RICHNESS Policy.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\ncreate_compliance_richness")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 7)
            LOGGER.debug("=================================")

    def test_create_compliance_dynamic_tolerance(self):
        """
        Test create_compliance_dynamic_tolerance
        """
        with testbook(
            "archivist/notebooks/Create Compliance DYNAMIC TOLERANCE Policy.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\ncreate_compliance_dynamic_tolerance")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 7)
            LOGGER.debug("=================================")

    @skip("Requires root access credentials - see #7742")
    def test_share_artist_asset_user(self):
        """
        Test share_artist_asset_user
        """
        with testbook(
            "archivist/notebooks/Sharing Artist Asset with User.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\nshare_artist_asset_user")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 7)
            LOGGER.debug("=================================")

    @skip("Requires root access credentials -- see #7742")
    def test_share_album_release_user(self):
        """
        Test share_album_release_user
        """
        with testbook(
            "archivist/notebooks/Sharing Album Release Info with User.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\nshare_album_release_user")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 7)
            LOGGER.debug("=================================")

    @skip("Requires root access credentials -- see #7742")
    def test_share_artist_asset_recordlabel(self):
        """
        Test share_artist_asset_recordlabel
        """
        with testbook(
            "archivist/notebooks/Sharing Artist Asset with Record Labels.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\nshare_artist_asset_recordlabel")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 7)
            LOGGER.debug("=================================")

    @skip("Requires root access credentials -- see #7742")
    def test_share_album_release_recordlabel(self):
        """
        Test share_album_release_recordlabel
        """
        with testbook(
            "archivist/notebooks/Sharing Album Release Info with Record Labels.ipynb",
            execute=True,
        ) as notebook:
            LOGGER.debug("\nshare_album_release_recordlabel")
            self.basic_notebook_test(notebook)
            self.check_notebook_cell(notebook, 7)
            LOGGER.debug("=================================")
