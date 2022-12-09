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
        self.archivist = setenv("TEST_ARCHIVIST", "https://app.rkvst.io")
        self.authtoken = setenv("TEST_AUTHTOKEN", "xxxxxxxxxxxxxxxxxxxx")
        self.client_id = setenv("TEST_CLIENT_ID", "yyyyyyyyyyyyyyyyyyyy")
        self.client_secret = setenv("TEST_CLIENT_SECRET", "zzzzzzzzzzzzzzzzzzzz")

    def tearDown(self):
        unsetenv("TEST_ARCHIVIST", self.archivist)
        unsetenv("TEST_AUTHTOKEN", self.authtoken)
        unsetenv("TEST_CLIENT_ID", self.client_id)
        unsetenv("TEST_CLIENT_SECRET", self.client_secret)

    def test_manage_credentials(self):
        """
        Test manage_credentials
        """
        with testbook(
            "archivist/notebooks/Manage_Credentials.ipynb", execute=True
        ) as notebook:
            self.assertEqual(
                notebook.ref("URL"),
                os.getenv("TEST_ARCHIVIST"),
                msg="Incorrect URL",
            )
            self.assertEqual(
                notebook.ref("auth_token"),
                os.getenv("TEST_AUTHTOKEN"),
                msg="Incorrect AUTHTOKEN",
            )
            self.assertEqual(
                notebook.cell_output_text(5),
                str(
                    Archivist(os.getenv("TEST_ARCHIVIST"), os.getenv("TEST_AUTHTOKEN"))
                ),
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
