"""
Test notebooks
"""
import os
from unittest import TestCase

from testbook import testbook

from archivist.archivist import Archivist

# pylint: disable=missing-function-docstring


def setenv(key, newvalue):
    val = os.getenv(key)
    os.environ[key] = newvalue
    return val


def unsetenv(key, oldvalue):
    if oldvalue is not None:
        os.environ[key] = oldvalue
    else:
        del os.environ[key]


class TestNotebooks(TestCase):
    """
    Test notebooks
    """

    def setUp(self):
        self.archivist = setenv("RKVST_URL", "https://app.rkvst.io")
        self.authtoken = setenv("RKVST_AUTHTOKEN", "xxxxxxxxxxxxxxxxxxxx")
        self.client_id = setenv("RKVST_APPREG_CLIENT", "yyyyyyyyyyyyyyyyyyyy")
        self.client_secret = setenv("RKVST_APPREG_SECRET", "zzzzzzzzzzzzzzzzzzzz")

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
                """client_id yyyyyyyyyyyyyyyyyyyy
client_secret zzzzzzzzzzzzzzzzzzzz""",
                msg="Incorrect client id and secret",
            )
            self.assertEqual(
                notebook.cell_output_text(7),
                "Archivist(https://app.rkvst.io)",
                msg="Incorrect Archivist",
            )
            self.assertEqual(
                notebook.cell_output_text(8),
                "Archivist(https://app.rkvst.io)",
                msg="Incorrect Archivist",
            )
