"""Summarize usage of RKVST and return estate for customer support purposes."""

# pylint: disable=too-many-locals

from os import environ, path, makedirs, remove, getcwd
from argparse import ArgumentParser
from json import dump as json_dump
from datetime import datetime
from shutil import move, make_archive

from archivist.archivist import Archivist
from archivist.logger import set_logger

# import archivist.dictmerge

# functions copied below because I was unable to import \
# them from dictmerge, I believe it is a conflict because I have a copy \
# of the SDK elsewhere on my computer


def assets_ext_attr(assets: list) -> list:
    """Create list of assets with extended attribute(s)"""
    extended_attributes_asset = []
    for asset in assets:
        for item in asset["attributes"]:
            if not item.startswith("arc_"):
                extended_attributes_asset.extend(asset)
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
            if not item.startswith("arc_"):
                extended_attributes_event.extend(event)
    return extended_attributes_event


def attachment_identities_events(events_with_attachments: list) -> list:
    """Create list of attachment identities"""
    total_attachments_events = set()
    for event in events_with_attachments:
        for item in event["event_attributes"]["arc_attachments"]:
            total_attachments_events.add(item["arc_attachment_identity"])
    return total_attachments_events


def main():
    """
    Summarize usage of RKVST.
    """

    parser = ArgumentParser(description="RKVST Diagnostic Tool")

    parser.add_argument(
        "--url", "-u", default="https://app.rkvst.io", help="RKVST URL to access"
    )
    parser.add_argument(
        "--client_id",
        "-c",
        default=environ.get("RKVST_CLIENT_ID"),
        help="Specify Application CLIENT_ID inline",
    )
    parser.add_argument(
        "--client_secret",
        "-s",
        default=environ.get("RKVST_CLIENT_SECRET"),
        help="Specify Application CLIENT_SECRET inline",
    )

    args = parser.parse_args()

    arch = Archivist(
        args.url,
        (args.client_id, args.client_secret),
    )

    props = {"confirmation_status": "CONFIRMED"}
    attrs = {}  # attributes can be added to filer by name, type, etc.

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

    # Create directories for output storage
    directory_a = "total_estate"
    directory_b = "assets_with_associated_events"
    parent_directory = path.abspath(getcwd())
    path_a = path.join(parent_directory, directory_a)
    path_b = path.join(path_a, directory_b)
    makedirs(path_a, exist_ok=True)
    makedirs(path_b, exist_ok=True)

    # Create a zip file containing detials of each asset, event, etc.
    estate_list = [assets, events, subjects, access_policies, summary_output]
    file_list = ["assets", "events", "subjects", "access_policies", "summary"]
    for item, name in zip(estate_list, file_list):
        with open(f"{name}.json", "w", encoding="utf8") as outfile:
            json_dump(item, outfile, indent=4)
        if path.exists(path.join(path_a, f"{name}.json")):
            remove(path.join(path_a, f"{name}.json"))
        move(path.join(parent_directory, f"{name}.json"), path_a)

    # Create folder with files for each asset and associated events.
    list_groups = []
    for asset in assets:
        event_list = []
        for event in events:
            #   if asset["identity"] == event["asset_identity"]:
            #      event_list.append(event)
            event_list = [
                e for e in events if asset["identity"] == event["asset_identity"]
            ]
        list_groups.append({str(asset["identity"]): event_list})

    for row in list_groups:
        file_name = [x.replace("/", "_") for x in row]
        with open(f"{file_name}.json", "w", encoding="utf8") as outfile:
            json_dump(row, outfile, indent=4)
        if path.exists(path.join(path_b, f"{file_name}.json")):
            remove(path.join(path_b, f"{file_name}.json"))
        move(path.join(parent_directory, f"{file_name}.json"), path_b)

    make_archive("total_estate", "zip", "total_estate")

    set_logger("DEBUG")


if __name__ == "__main__":
    main()
