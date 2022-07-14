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
    extended_attributes_asset = []
    for asset in assets:
        for item in asset["attributes"]:
            if not item.startswith("arc_") and asset not in extended_attributes_asset:
                extended_attributes_asset.append(asset)
    return extended_attributes_asset


def attachment_identities_assets(assets_with_attachments: list) -> list:
    """Create list of attachment identities"""
    total_attachments_assets = set()
    for asset in assets_with_attachments:
        for item in asset["attributes"]["arc_attachments"]:
            total_attachments_assets.add(item["arc_attachment_identity"])
    return total_attachments_assets


def events_ext_attr(events: list) -> list:
    """Create list of events with extended attribute(s)"""
    extended_attributes_event = []
    for event in events:
        for item in event["event_attributes"]:
            if not item.startswith("arc_") and event not in extended_attributes_event:
                extended_attributes_event.append(event)
    return extended_attributes_event


def attachment_identities_events(events_with_attachments: list) -> list:
    """Create list of attachment identities"""
    total_attachments_events = set()
    for event in events_with_attachments:
        for item in event["event_attributes"]["arc_attachments"]:
            total_attachments_events.add(item["arc_attachment_identity"])
    return total_attachments_events
