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
            if "arc_" not in item and asset not in extended_attributes_asset:
                extended_attributes_asset.append(asset)
    return extended_attributes_asset


def attachment_identities_assets(assets_with_attachments: list) -> list:
    """Create list of attachment identities"""
    global total_attachments_assets
    total_attachments_assets = []
    for asset in assets_with_attachments:
        total_attachments_assets.append(
            [
                item["arc_attachment_identity"]
                for item in asset["attributes"]["arc_attachments"]
                if item["arc_attachment_identity"] not in total_attachments_assets
            ]
        )
    return total_attachments_assets


def events_ext_attr(events: list) -> list:
    """Create list of events with extended attribute(s)"""
    global extended_attributes_event
    extended_attributes_event = []
    for event in events:
        for item in event["event_attributes"]:
            if "arc_" not in item and event not in extended_attributes_event:
                extended_attributes_event.append(event)
    return extended_attributes_event


def attachment_identities_events(events_with_attachments: list) -> list:
    """Create list of attachment identities"""
    global total_attachments_events
    total_attachments_events = []
    for event in events_with_attachments:
        total_attachments_events.append(
            [
                item["arc_attachment_identity"]
                for item in event["event_attributes"]["arc_attachments"]
                if item["arc_attachment_identity"] not in total_attachments_events
            ]
        )
    return total_attachments_events


def level_1_sanitization(dct: dict) -> dict:
    def modify_key(k, v):
        return k

    def modify_value(k, v):
        return "#" * len(v) if "arc_" not in k else v

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}


def level_2_sanitization(dct: dict) -> dict:
    def modify_key(k, v):
        return k

    def modify_value(k, v):
        return "#" * len(v) if v else v

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}


def level_3_sanitization(dct: dict) -> dict:
    def modify_key(k, v):
        return "#" * len(k) if "arc_" not in k else k

    def modify_value(k, v):
        return "#" * len(v) if v else v

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}


def level_4_sanitization(dct: dict) -> dict:
    def modify_key(k, v):
        return "#" * len(k) if k else k

    def modify_value(k, v):
        return "#" * len(v) if v else v

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}


def level_5_sanitization(dct: dict) -> dict:
    def modify_key(k, v):
        return None

    def modify_value(k, v):
        return None

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}
