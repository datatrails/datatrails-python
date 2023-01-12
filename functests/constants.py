"""
hide docstringss
"""
# pylint: disable=missing-docstring
import unittest


class TestCase(unittest.TestCase):
    #  ....
    def shortDescription(self):
        return None
