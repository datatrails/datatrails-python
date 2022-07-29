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


def _dotdict(dct: Optional[dict]) -> Optional[dict]:
    """Emit nested dictionary as dot delimited dict with one level"""
    if dct is None:
        return None
    return flatten(dct, reducer="dot")


def assets_ext_attr(assets: list) -> list:
    """Create list of assets with extended attribute(s)"""
    extended_attributes_asset = [
        asset
        for asset in assets
        if any(not item.startswith("arc_") for item in asset["attributes"])
    ]
    return extended_attributes_asset


def events_ext_attr(events: list) -> list:
    """Create list of events with extended attribute(s)"""
    extended_attributes_event = [
        event
        for event in events
        if any(not item.startswith("arc_") for item in event["event_attributes"])
    ]
    return extended_attributes_event


def assets_location(assets: list) -> list:
    """Filter assets down to those with an associated location ID."""
    assets_with_location = [
        asset
        for asset in assets
        if asset["attributes"].get("arc_home_location_identity", [])
    ]
    return assets_with_location


def assets_attachment(assets: list) -> list:
    """Filter assets down to those with an associated attachment ID."""
    assets_with_attachment = [
        asset for asset in assets if asset["attributes"].get("arc_attachments", [])
    ]
    return assets_with_attachment


def events_attachment(events: list) -> list:
    """Filter assets down to those with an associated attachment."""
    events_with_attachment = [
        event
        for event in events
        if event["event_attributes"].get("arc_attachments", [])
    ]
    return events_with_attachment
