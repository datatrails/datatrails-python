#!/usr/bin/python3

"""
Test sbom release process
"""

# pylint: disable=fixme

from json import dumps as json_dumps
from os import getenv
from warnings import filterwarnings

from archivist.archivist import Archivist
from archivist.assets import BEHAVIOURS
from archivist.constants import SBOM_PACKAGE, SBOM_RELEASE
from archivist.proof_mechanism import ProofMechanism
from archivist.utils import get_auth

filterwarnings("ignore", message="Unverified HTTPS request")

ASSET_NAME = "RKVST SaaS Software Package"


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
            "behaviours": BEHAVIOURS,
            "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
            "attributes": {
                "arc_display_name": ASSET_NAME,
                "arc_display_type": SBOM_PACKAGE,
                "arc_description": "Software Package for RKVST SaaS",
            },
        },
        confirm=True,
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
                "arc_description": f"Jitsuin Inc RKVST SAAS Release {release}",
                "arc_display_type": SBOM_RELEASE,
            },
            "attachments": [
                {
                    "filename": f"{sbom_filename}",
                    "content_type": "text/xml",
                    "display_name": f"RKVST {release} SBOM",
                    "type": SBOM_RELEASE,
                },
            ],
        },
        confirm=True,
    )
    print("##[debug]Release:\n", json_dumps(event, indent=4))

    return (asset, event)


def main():
    """
    main entry point
    """

    rkvst_url = getenv("RKVST_URL")

    auth = get_auth(
        auth_token_filename=getenv("AUTHTOKEN_FILENAME"),
        client_id=getenv("CLIENT_ID"),
        client_secret_filename=getenv("CLIENT_SECRET_FILENAME"),
    )

    arch = Archivist(rkvst_url, auth, verify=False, max_time=300)

    asset, event = sbom_release(
        arch, getenv("BUILD_BUILDNUMBER"), getenv("SBOM_FILEPATH")
    )

    rkvst_path = "archivist/v2"

    asset_url = f"{rkvst_url}/{rkvst_path}/{asset['identity']}"
    event_url = f"{rkvst_url}/{rkvst_path}/{event['identity']}"

    print(f"##vso[task.setvariable variable=RKVST_ASSET_URL]{asset_url}")
    print(f"##vso[task.setvariable variable=RKVST_EVENT_URL]{event_url}")
    print(f"##[debug]Asset url: {asset_url}")
    print(f"##[debug]Event url: {event_url}")


if __name__ == "__main__":
    main()
