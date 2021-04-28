"""Timestamp manipulation"""

import iso8601
import rfc3339


def parse_timestamp(date_string):
    """Parse an Archivist timestamp to a datetime object"""
    return iso8601.parse_date(date_string)


def make_timestamp(date_object):
    """Format a datetime object into an Archivist format
    timestamp string"""
    return rfc3339.rfc3339(date_object)
