"""Archivist dict deep merge
"""
from __future__ import annotations
from copy import deepcopy
from typing import Any, Optional

from flatten_dict import flatten, unflatten


def _deepmerge(
    dct1: Optional[dict[str, Any]], dct2: Optional[dict[str, Any]]
) -> dict[str, Any]:
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


def _dotdict(dct: Optional[dict[str, Any]]) -> dict[str, str] | None:
    """Emit nested dictionary as dot delimited dict with one level"""
    if dct is None:
        return None
    return flatten(dct, reducer="dot")
