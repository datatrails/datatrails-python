"""
Test assets attachments scanning
"""

from datetime import date, datetime, timedelta
from json import dumps as json_dumps
from os import getenv
from sys import exit as sys_exit
from warnings import filterwarnings

from archivist.archivist import Archivist
from archivist.assets import BEHAVIOURS
from archivist.proof_mechanism import ProofMechanism
from archivist.utils import get_auth

filterwarnings("ignore", message="Unverified HTTPS request")


def scan_test(arch, datestring, scanned_expected=False):
    """
    Test asset creation if not exists - check attachment for scanned status.

    Because we use create_if_not_exists the asset and attachments will persist.

    The test checks the scanned timestamp and checks scanned status.
    The first attachment should return OK after 24 hours and the second attachment
    should return bad after 24 hours.

    Args:

         date (str): date string of the form 2022-03-01
         scanned_expected (bool): whether the attachment is expected to have been scanned
            - true for yesterday
    """

    ASSET_NAME = (
        f"Scan test asset with 2 attachments - one bad or not scanned {datestring}"
    )

    print(f"##[debug]Checking asset {ASSET_NAME}")

    asset, existed = arch.assets.create_if_not_exists(
        {
            "selector": [
                {
                    "attributes": [
                        "arc_display_name",
                        "arc_namespace",
                    ],
                },
            ],
            "behaviours": BEHAVIOURS,
            "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
            "attributes": {
                "arc_display_name": ASSET_NAME,
                "arc_namespace": "namespace",
                "arc_firmware_version": "1.0",
                "arc_serial_number": "vtl-x4-07",
                "arc_description": "Traffic flow control light at A603 North East",
                "arc_display_type": "Traffic light with violation camera",
                "some_custom_attribute": "value",
            },
            "attachments": [
                {
                    "url": (
                        "https://raw.githubusercontent.com/jitsuin-inc/archivist-python/"
                        "main/functests/test_resources/telephone.jpg"
                    ),
                    "content_type": "image/jpg",
                },
                {
                    "url": "https://secure.eicar.org/eicarcom2.zip",
                    "content_type": "application/zip",
                },
            ],
        },
        confirm=True,
    )
    print("asset", json_dumps(asset, indent=4))
    print("existed", existed)

    fails = []

    # first attachment should be clean....
    attachment_id = asset["attributes"]["arc_attachments"][0]["arc_attachment_identity"]
    info = arch.attachments.info(
        attachment_id,
        asset_or_event_id=asset["identity"],
    )
    print("info attachment1", json_dumps(info, indent=4))

    timestamp = info["scanned_timestamp"]
    if timestamp:
        print(attachment_id, "scanned last at", timestamp)
        print(attachment_id, "scanned status", info["scanned_status"])
        print(attachment_id, "scanned reason", info["scanned_bad_reason"])
        if info["scanned_status"] != "SCANNED_OK":
            fails.append("First attachment should be clean.")
    elif scanned_expected:
        fails.append("Yesterday's first attachment has not been scanned.")

    # second attachment should be bad when scanned....
    attachment_id = asset["attributes"]["arc_attachments"][1]["arc_attachment_identity"]
    info = arch.attachments.info(
        attachment_id,
        asset_or_event_id=asset["identity"],
    )
    print("info attachment2", json_dumps(info, indent=4))
    timestamp = info["scanned_timestamp"]
    if timestamp:
        print(attachment_id, "scanned last at", timestamp)
        print(attachment_id, "scanned reason", info["scanned_bad_reason"])
        if info["scanned_status"] != "SCANNED_BAD":
            fails.append("Second attachment should not be clean")
    elif scanned_expected:
        fails.append("Yesterday's second attachment has not been scanned.")

    num_fails = len(fails)
    if num_fails > 0:
        print(f"##[error]There are {num_fails} test failures")
        for fail in fails:
            print(f"##[debug]{fail}")
        sys_exit(1)


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

    print("##[group]Today")
    today = date.today()
    scan_test(arch, today.strftime("%Y-%m-%d"))

    # currently scans run mon-fri
    # so if today is mon, previous day is fri, otherwise previous day is yesterday
    print("##[group]Previous day")
    days_delta = 3 if today.strftime("%a") == "Mon" else 1
    previous_day = datetime.now() - timedelta(days=days_delta)
    scan_test(arch, previous_day.strftime("%Y-%m-%d"), scanned_expected=True)


if __name__ == "__main__":
    main()
