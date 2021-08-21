"""Archivist dict deep merge
"""

from copy import deepcopy

from flatten_dict import flatten, unflatten


def _deepmerge(dct1: dict, dct2: dict) -> dict:
    """Deep merge 2 dictionaries

    The settings from dct2 overwrite or add to dct1
    """
    if dct1 is None:
        return deepcopy(dct2)

    return unflatten({**flatten(dct1), **flatten(dct2)})


def _dotstring(dct: dict) -> str:
    """Emit nested dictionary as dot delimited string"""
    return flatten(dct, reducer="dot").items()
