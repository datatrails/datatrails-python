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


def sbom_release(arch, release, sbom_filename):  # XXX instead of filename may be URL?
    """
    Test sbom release process

    Because we use create_if_not_exists the software package asset and attachments will persist.

    Args:
        release (str): release string of form YYYYMMDD.N
    """

    ASSET_NAME = "RKVST SAAS Software Package"

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
                "arc_description": "Software Package for RKVST SAAS",
                "acme_sbom_license": "www.gnu.org/licenses/gpl.txt",  # XXX
                "acme_proprietary_secret": "For your eyes only",  # XXX
            },
            # the attachment should be the RKVST logo? - change accordingly XXX
            "attachments": [
                {
                    "url": (
                        "https://raw.githubusercontent.com/jitsuin-inc/archivist-python/"
                        "main/functests/test_resources/telephone.jpg",
                    ),
                    "content_type": "image/jpg",
                },
            ],
        },
        confirm=True,
    )
    print("asset", json_dumps(asset, indent=4))
    print("existed", existed)

    # Releasing an SBOM
    event = arch.events.create_from_data(
        asset["identity"],
        {
            "operation": "Record",
            "behaviour": "RecordEvidence",
            "event_attributes": {
                "arc_description": f"Jitsuin Inc RKVST SAAS Released {release}",
                "arc_display_type": SBOM_RELEASE,
            },
            "attachments": [
                {
                    "filename": f"{sbom_filename}",  # XXX maybe change to URL?
                    "content_type": "text/xml",
                    "display_name": f"RKVST {release} SBOM",
                    "type": SBOM_RELEASE,
                },
            ],
        },
        confirm=True,
    )
    print("release", json_dumps(event, indent=4))
    event = arch.events.list(
        asset_id=asset["identity"],
        props={"confirmation_status": "CONFIRMED"},
        attrs={"arc_display_type": SBOM_RELEASE},
    )


def main():
    """
    main entry point
    """
    auth = get_auth(
        auth_token_filename=getenv("TEST_AUTHTOKEN_FILENAME"),
        client_id=getenv("TEST_CLIENT_ID"),
        client_secret_filename=getenv("TEST_CLIENT_SECRET_FILENAME"),
    )

    arch = Archivist(getenv("TEST_ARCHIVIST"), auth, verify=False, max_time=300)

    # XXX: change these accordingly - filename may be a url?
    sbom_release(arch, "YYYYMMDD.N", "tmp/rkvst_saas_YYYYMMDD.N")


if __name__ == "__main__":
    main()
