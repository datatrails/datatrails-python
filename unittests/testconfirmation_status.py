"""
Test confirmation status
"""

# pylint: disable=protected-access

from unittest import TestCase

from archivist.confirmation_status import ConfirmationStatus


class TestConfirmationStatus(TestCase):
    """
    Test confirmation status for archivist
    """

    def assert_confirmation_status(self, name, index):
        """
        Test confirmation_status
        """
        self.assertEqual(ConfirmationStatus(index).name, name, msg="Incorrect name")
        self.assertEqual(ConfirmationStatus[name].value, index, msg="Incorrect index")

    def test_confirmation_status_unspecified(self):
        """
        Test confirmation_status
        """
        self.assertEqual(ConfirmationStatus.UNSPECIFIED.value, 0, msg="Incorrect value")
        self.assertEqual(
            ConfirmationStatus.UNSPECIFIED.name, "UNSPECIFIED", msg="Incorrect value"
        )
        self.assert_confirmation_status("UNSPECIFIED", 0)

    def test_confirmation_status_pending(self):
        """
        Test confirmation_status
        """
        self.assertEqual(ConfirmationStatus.PENDING.value, 1, msg="Incorrect value")
        self.assertEqual(
            ConfirmationStatus.PENDING.name, "PENDING", msg="Incorrect value"
        )
        self.assert_confirmation_status("PENDING", 1)

    def test_confirmation_status_confirmed(self):
        """
        Test confirmation_status
        """
        self.assertEqual(ConfirmationStatus.CONFIRMED.value, 2, msg="Incorrect value")
        self.assertEqual(
            ConfirmationStatus.CONFIRMED.name, "CONFIRMED", msg="Incorrect value"
        )
        self.assert_confirmation_status("CONFIRMED", 2)

    def test_confirmation_status_failed(self):
        """
        Test confirmation_status
        """
        self.assertEqual(ConfirmationStatus.FAILED.value, 3, msg="Incorrect value")
        self.assertEqual(
            ConfirmationStatus.FAILED.name, "FAILED", msg="Incorrect value"
        )
        self.assert_confirmation_status("FAILED", 3)

    def test_confirmation_status_stored(self):
        """
        Test confirmation_status
        """
        self.assertEqual(ConfirmationStatus.STORED.value, 4, msg="Incorrect value")
        self.assertEqual(
            ConfirmationStatus.STORED.name, "STORED", msg="Incorrect value"
        )
        self.assert_confirmation_status("STORED", 4)

    def test_confirmation_status_committed(self):
        """
        Test confirmation_status
        """
        self.assertEqual(ConfirmationStatus.COMMITTED.value, 5, msg="Incorrect value")
        self.assertEqual(
            ConfirmationStatus.COMMITTED.name, "COMMITTED", msg="Incorrect value"
        )
        self.assert_confirmation_status("COMMITTED", 5)

    def test_confirmation_status_unequivocal(self):
        """
        Test confirmation_status
        """
        self.assertEqual(ConfirmationStatus.UNEQUIVOCAL.value, 6, msg="Incorrect value")
        self.assertEqual(
            ConfirmationStatus.UNEQUIVOCAL.name, "UNEQUIVOCAL", msg="Incorrect value"
        )
        self.assert_confirmation_status("UNEQUIVOCAL", 6)

    def test_confirmation_status_length(self):
        """
        Test confirmation_status
        """
        self.assertEqual(len(ConfirmationStatus), 7, msg="Incorrect value")
