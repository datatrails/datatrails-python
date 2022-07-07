"""
Test about method
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

from unittest import TestCase

from archivist import about


class TestAbout(TestCase):
    """
    Test about
    """

    def test_about(self):
        """
        Test about
        """
        self.assertGreater(
            len(about.__version__),
            0,
            msg="about version should be populated",
        )
