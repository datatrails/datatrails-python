#!/usr/bin/python3

"""
Test sbom release process
"""

# pylint: disable=fixme

from json import dumps as json_dumps
from os import getenv
from warnings import filterwarnings

from archivist.archivist import Archivist
from archivist.constants import ASSET_BEHAVIOURS, SBOM_PACKAGE, SBOM_RELEASE
from archivist.utils import get_auth

filterwarnings("ignore", message="Unverified HTTPS request")

ASSET_NAME = "DataTrails SaaS Software Package"


def sbom_release(arch, release, sbom_filename):
    """
    Test sbom release process

    Because we use create_if_not_exists the software package asset will persist.

    Args:
        release (str): release string of form YYYYMMDD.N
        sbom_filename (str): name of sbom file
    """

    print(f"##[debug]Creating software package {ASSET_NAME}")

    asset, existed = arch.assets.create_if_not_exists(
        {
            "selector": [
                {
                    "attributes": [
                        "arc_display_name",
                    ],
                },
            ],
            "behaviours": ASSET_BEHAVIOURS,
            "attributes": {
                "arc_display_name": ASSET_NAME,
                "arc_display_type": SBOM_PACKAGE,
                "arc_description": "Software Package for DataTrails SaaS",
            },
        },
    )
    print("##[debug]Asset:\n", json_dumps(asset, indent=4))
    print("##[debug]Existed:", existed)

    print("")

    # Releasing an SBOM
    event = arch.events.create_from_data(
        asset["identity"],
        {
            "operation": "Record",
            "behaviour": "RecordEvidence",
            "event_attributes": {
                "arc_description": f"DataTrails Inc DataTrails SAAS Release {release}",
                "arc_display_type": SBOM_RELEASE,
            },
            "attachments": [
                {
                    "filename": f"{sbom_filename}",
                    "content_type": "text/xml",
                    "display_name": f"DataTrails {release} SBOM",
                    "type": SBOM_RELEASE,
                },
            ],
        },
    )
    print("##[debug]Release:\n", json_dumps(event, indent=4))

    return (asset, event)


def main():
    """
    main entry point
    """

    datatrails_url = getenv("DATATRAILS_URL")

    auth = get_auth(
        auth_token=getenv("DATATRAILS_AUTHTOKEN"),
        auth_token_filename=getenv("DATATRAILS_AUTHTOKEN_FILENAME"),
        client_id=getenv("DATATRAILS_APPREG_CLIENT"),
        client_secret=getenv("DATATRAILS_APPREG_SECRET"),
        client_secret_filename=getenv("DATATRAILS_APPREG_SECRET_FILENAME"),
    )

    with Archivist(datatrails_url, auth, max_time=300) as arch:
        asset, event = sbom_release(
            arch, getenv("BUILD_BUILDNUMBER"), getenv("SBOM_FILEPATH")
        )

        datatrails_path = "archivist/v2"

        asset_url = f"{datatrails_url}/{datatrails_path}/{asset['identity']}"
        event_url = f"{datatrails_url}/{datatrails_path}/{event['identity']}"

        print(f"##vso[task.setvariable variable=DATATRAILS_ASSET_URL]{asset_url}")
        print(f"##vso[task.setvariable variable=DATATRAILS_EVENT_URL]{event_url}")
        print(f"##[debug]Asset url: {asset_url}")
        print(f"##[debug]Event url: {event_url}")


if __name__ == "__main__":
    main()
