"""
Test archivist
"""

# pylint: disable=attribute-defined-outside-init
# pylint: disable=missing-docstring
# pylint: disable=too-few-public-methods

from unittest import TestCase, mock

from archivist import timestamp


class TestTimestamp(TestCase):
    """
    Test timestamp
    """

    @mock.patch('archivist.timestamp.iso8601.parse_date')
    def test_parse_timestamp(self, mock_parse_date):
        """
        Test parse_timestamp
        """
        unused = timestamp.parse_timestamp('date_string')
        self.assertEqual(
            tuple(mock_parse_date.call_args),
            mock.call('date_string'),
            msg="parse_timestamp called with incorrect argument",
        )

    @mock.patch('archivist.timestamp.rfc3339.rfc3339')
    def test_make_timestamp(self, mock_rfc3339):
        """
        Test parse_timestamp
        """
        unused = timestamp.make_timestamp('date_string')
        self.assertEqual(
            tuple(mock_rfc3339.call_args),
            mock.call('date_string'),
            msg="make_timestamp called with incorrect argument",
        )
