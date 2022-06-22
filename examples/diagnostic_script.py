"""Summarize usage of RKVST and return estate for customer support purposes."""

import os
import argparse
import json
from datetime import datetime
import shutil

from archivist.archivist import Archivist
from archivist.logger import set_logger
import archivist.dictmerge

# functions copied below because I was unable to import \
# them from dictmerge, I believe it is a conflict because I have a copy \
# of the SDK elsewhere on my computer


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
    """Sanitize values of attributes with custom keys."""

    def modify_key(k, v):
        return k

    def modify_value(k, v):
        return "#" * len(v) if "arc_" not in k else v

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}


def level_2_sanitization(dct: dict) -> dict:
    """Sanitize all attribute values."""

    def modify_key(k, v):
        return k

    def modify_value(k, v):
        return "#" * len(v) if v else v

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}


def level_3_sanitization(dct: dict) -> dict:
    """Sanitize all attribute values and all custom keys."""

    def modify_key(k, v):
        return "#" * len(k) if "arc_" not in k else k

    def modify_value(k, v):
        return "#" * len(v) if v else v

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}


def level_4_sanitization(dct: dict) -> dict:
    """Sanitize all attribute keys and values."""

    def modify_key(k, v):
        return "#" * len(k) if k else k

    def modify_value(k, v):
        return "#" * len(v) if v else v

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}


def level_5_sanitization(dct: dict) -> dict:
    """Replace attribute dictionary with None."""

    def modify_key(k, v):
        return None

    def modify_value(k, v):
        return None

    return {modify_key(k, v): modify_value(k, v) for k, v in dct.items()}


def main():
    """
    Summarize usage of RKVST.
    """

    parser = argparse.ArgumentParser(description="RKVST Diagnostic Tool")

    parser.add_argument(
        "--url", "-u", default="https://app.rkvst.io", help="RKVST URL to access"
    )
    parser.add_argument(
        "--client_id",
        "-c",
        default=os.environ.get("RKVST_CLIENT_ID"),
        help="Specify Application CLIENT_ID inline",
    )
    parser.add_argument(
        "--client_secret",
        "-s",
        default=os.environ.get("RKVST_CLIENT_SECRET"),
        help="Specify Application CLIENT_SECRET inline",
    )

    args = parser.parse_args()

    arch = Archivist(
        args.url,
        (args.client_id, args.client_secret),
    )

    props = {"confirmation_status": "CONFIRMED"}
    attrs = {}  # attributes can be added to filer by name, type, etc.

    # Specify if you would like estate details returned along with usage summary
    return_estate = True
    sanitization = "Level 5"

    # Total Number of Assets
    assets = list(arch.assets.list(props=props, attrs=attrs))

    # Assets with Extended Attributes
    extended_attributes_asset = assets_ext_attr(assets)

    # Assets with Associated Location
    assets_with_location = list(
        arch.assets.list(
            props=props,
            attrs=dict(
                list(attrs.items()) + list({"arc_home_location_identity": "*"}.items())
            ),
        )
    )

    # Assets with Attachments
    assets_with_attachments = list(
        arch.assets.list(
            props=props,
            attrs=dict(list(attrs.items()) + list({"arc_attachments": "*"}.items())),
        )
    )
    total_attachments_assets = attachment_identities_assets(assets_with_attachments)

    # Total Number of Events
    events = list(arch.events.list(props=props, attrs=attrs))

    # Events with Extended Attributes
    extended_attributes_event = events_ext_attr(events)

    # Events with Attachments
    events_with_attachments = list(
        arch.events.list(
            props=props,
            attrs=dict(list(attrs.items()) + list({"arc_attachments": "*"}.items())),
        )
    )
    total_attachments_events = attachment_identities_events(events_with_attachments)

    # Average Events per Asset
    avg_events_per_asset = len(events) / len(assets)

    # Total Number of Subjects
    subjects = list(arch.subjects.list())

    # Total Number of Access Policies
    access_policies = list(arch.access_policies.list())

    summary_output = {
        "Date of Scan": str(datetime.now()),
        "Number of Assets": len(assets),
        "Assets with Extended Attributes": len(extended_attributes_asset),
        "Assets with Associated Location": len(assets_with_location),
        "Number of Events": len(events),
        "Events with Extended Attributes": len(extended_attributes_event),
        "Events with Attachments": len(events_with_attachments),
        "Average Events per Asset": round(avg_events_per_asset),
        "Total Number of Attachments": len(total_attachments_assets)
        + len(total_attachments_events),
        "Number of Subjects": len(subjects),
        "Number of Access Policies": len(access_policies),
    }

    if return_estate is True:
        for asset in assets:
            for event in events:
                if sanitization == "Level 1":
                    asset["attributes"] = level_1_sanitization(asset["attributes"])
                    event["event_attributes"] = level_1_sanitization(
                        event["event_attributes"]
                    )
                    event["asset_attributes"] = level_1_sanitization(
                        event["asset_attributes"]
                    )
                if sanitization == "Level 2":
                    asset["attributes"] = level_2_sanitization(asset["attributes"])
                    event["event_attributes"] = level_2_sanitization(
                        event["event_attributes"]
                    )
                    event["asset_attributes"] = level_2_sanitization(
                        event["asset_attributes"]
                    )
                if sanitization == "Level 3":
                    asset["attributes"] = level_3_sanitization(asset["attributes"])
                    event["event_attributes"] = level_3_sanitization(
                        event["event_attributes"]
                    )
                    event["asset_attributes"] = level_3_sanitization(
                        event["asset_attributes"]
                    )
                if sanitization == "Level 4":
                    asset["attributes"] = level_4_sanitization(asset["attributes"])
                    event["event_attributes"] = level_4_sanitization(
                        event["event_attributes"]
                    )
                    event["asset_attributes"] = level_4_sanitization(
                        event["asset_attributes"]
                    )
                if sanitization == "Level 5":
                    asset["attributes"] = level_5_sanitization(asset["attributes"])
                    event["event_attributes"] = level_5_sanitization(
                        event["event_attributes"]
                    )
                    event["asset_attributes"] = level_5_sanitization(
                        event["asset_attributes"]
                    )

    # Create directories for output storage
    directory_a = "total_estate"
    directory_b = "assets_with_associated_events"
    parent_directory = os.path.abspath(os.getcwd())
    path_a = os.path.join(parent_directory, directory_a)
    path_b = os.path.join(path_a, directory_b)
    os.makedirs(path_a, exist_ok=True)
    os.makedirs(path_b, exist_ok=True)

    # Create a zip file containing detials of each asset, event, etc.
    estate_list = [assets, events, subjects, access_policies, summary_output]
    file_list = ["assets", "events", "subjects", "access_policies", "summary"]
    for item, name in zip(estate_list, file_list):
        with open(f"{name}.json", "w", encoding="utf8") as outfile:
            json.dump(item, outfile, indent=4)
        if os.path.exists(os.path.join(path_a, f"{name}.json")):
            os.remove(os.path.join(path_a, f"{name}.json"))
        shutil.move(os.path.join(parent_directory, f"{name}.json"), path_a)

    # Create folder with files for each asset and associated events.
    list_groups = []
    for asset in assets:
        event_list = []
        for event in events:
            if asset["identity"] == event["asset_identity"]:
                event_list.append(event)
        list_groups.append({str(asset["identity"]): event_list})

    for row in list_groups:
        file_name = [x.replace("/", "_") for x in row]
        with open(f"{file_name}.json", "w", encoding="utf8") as outfile:
            json.dump(row, outfile, indent=4)
        if os.path.exists(os.path.join(path_b, f"{file_name}.json")):
            os.remove(os.path.join(path_b, f"{file_name}.json"))
        shutil.move(os.path.join(parent_directory, f"{file_name}.json"), path_b)

    shutil.make_archive("total_estate", "zip", "total_estate")

    set_logger("DEBUG")


if __name__ == "__main__":
    main()
