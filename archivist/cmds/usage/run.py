"""Run RKVST usage summary script."""

from contextlib import suppress
from logging import getLogger
from sys import exit as sys_exit

from os import path, makedirs, remove, getcwd
from json import dump as json_dump
from datetime import datetime
from shutil import move, make_archive

from archivist.dictmerge import (
    assets_attachment,
    assets_ext_attr,
    assets_location,
    events_ext_attr,
    events_attachment,
)

LOGGER = getLogger(__name__)


def run(arch, args):
    """Run diagnostic script."""
    props = {"confirmation_status": "CONFIRMED"}
    attrs = {}  # attributes can be added to filer by name, type, etc.

    # Total Number of Assets
    assets = list(arch.assets.list(props=props, attrs=attrs))

    # Assets with Extended Attributes
    extended_attributes_asset = assets_ext_attr(assets)

    # Assets with Associated Location
    assets_with_location = assets_location(assets)

    # Assets with Attachments
    assets_with_attachments = assets_attachment(assets)

    # Total Number of Events
    events = list(arch.events.list(props=props, attrs=attrs))

    # Events with Extended Attributes
    extended_attributes_event = events_ext_attr(events)

    # Events with Attachments
    events_with_attachments = events_attachment(events)

    # Average Events per Asset
    avg_events_per_asset = len(events) / len(assets)

    # Total Number of Subjects
    subjects = list(arch.subjects.list())

    # Total Number of Access Policies
    access_policies = list(arch.access_policies.list())

    # Total Number of Compliance Policies
    compliance_policies = list(arch.compliance_policies.list())

    summary_output = {
        "Date of Scan": str(datetime.now()),
        "Number of Assets": len(assets),
        "Assets with Extended Attributes": len(extended_attributes_asset),
        "Assets with Associated Location": len(assets_with_location),
        "Number of Events": len(events),
        "Events with Extended Attributes": len(extended_attributes_event),
        "Events with Attachments": len(events_with_attachments),
        "Average Events per Asset": round(avg_events_per_asset),
        "Total Number of Attachments": len(assets_with_attachments)
        + len(events_with_attachments),
        "Number of Subjects": len(subjects),
        "Number of Access Policies": len(access_policies),
        "Number of Compliance Policies": len(compliance_policies),
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
    estate_list = [
        assets,
        events,
        subjects,
        access_policies,
        compliance_policies,
        summary_output,
    ]
    file_list = [
        "assets",
        "events",
        "subjects",
        "access_policies",
        "compliance_policies",
        "summary",
    ]
    for item, name in zip(estate_list, file_list):
        with open(f"{name}.json", "w", encoding="utf8") as outfile:
            json_dump(item, outfile, indent=4)
        with suppress(FileNotFoundError):
            remove(path.join(path_a, f"{name}.json"))
        move(path.join(parent_directory, f"{name}.json"), path_a)

    # Create folder with files for each asset and associated events.
    list_groups = []
    for asset in assets:
        for event in events:
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

    sys_exit(0)
