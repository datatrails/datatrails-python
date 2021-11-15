"""Timestamp manipulation

   Defines timestamp policy for Archivist.

"""

from datetime import datetime
from iso8601 import parse_date
from rfc3339 import rfc3339


def parse_timestamp(date_string):
    """Parse an Archivist timestamp to a datetime object

    See https://pypi.org/project/iso8601/

    Args:
        date_string (str): a string representing date and time in ISO8601 format.

    Returns:
        datetime object

    """
    return parse_date(date_string)


def make_timestamp(date_object):
    """Format a datetime object into an Archivist format timestamp string

    See https://pypi.org/project/rfc3339/

    Args:
        datetime (datetime): datetime object

    Returns:
        string representation of time

    """
    return rfc3339(date_object, utc=True, use_system_timezone=False)


def now_timestamp():
    """Return Now as an Archivist format timestamp string

    See https://pypi.org/project/rfc3339/

    Returns:
        string representation of now

    """
    return make_timestamp(datetime.now())
