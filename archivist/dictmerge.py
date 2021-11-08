"""Archivist dict deep merge
"""

from copy import deepcopy
from typing import Optional

from flatten_dict import flatten, unflatten


def _deepmerge(dct1: Optional[dict], dct2: Optional[dict]) -> dict:
    """Deep merge 2 dictionaries

    The settings from dct2 overwrite or add to dct1
    """
    if dct1 is None:
        if dct2 is None:
            return {}
        return deepcopy(dct2)

    if dct2 is None:
        return deepcopy(dct1)

    return unflatten({**flatten(dct1), **flatten(dct2)})


def _dotstring(dct: dict):
    """Emit nested dictionary as dot delimited string"""
    return flatten(dct, reducer="dot").items()
