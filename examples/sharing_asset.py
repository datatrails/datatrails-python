"""Create an asset for Archivist with token.

   Create an access_policy that shares an asset when certain criteria are met.

   Access the asset from another Archivist connection using a second token with different
   access rights.
"""

from json import dumps as json_dumps
from os import getenv
from warnings import filterwarnings

from archivist.archivist import Archivist
from archivist.constants import ASSET_BEHAVIOURS, SUBJECTS_SELF_ID
from archivist.logger import set_logger
from archivist.utils import get_auth

filterwarnings("ignore", message="Unverified HTTPS request")


def create_example_asset(arch, label):
    """Create an asset using Archivist Connection.

    Args:
        arch: archivist connection.
        label: convenience label to easily distinguish the 2 organizations.

    Returns:
        Asset: a new asset created.

    """
    attrs = {
        "arc_display_name": f"{label}_display_name",  # Asset's display name
        "arc_description": f"{label}_display_description",  # Asset's description
        "arc_display_type": f"{label}_display_type",  # Arc_display_type is a free text field
        "ext_vendor_name": label,
    }

    # The first argument is the attributes of the asset
    #
    return arch.assets.create(attrs=attrs)


def create_archivist(label):
    """Create connection to archivist"""
    # Get authorization token. The token grants certain rights and access permissions.
    # The token can represent the root principal or user in an organization. Different tokens
    # could indicate different users in the same organization or membership of different
    # organiastions.
    auth = get_auth(
        auth_token=getenv(f"DATATRAILS_AUTHTOKEN_{label}"),
    )
    # Initialize connection to Archivist. max_time is the time to wait for confirmation
    # of an asset or event creation - the default is 300 seconds but one can optionally
    # specify a different value.
    return Archivist(
        "https://app.datatrails.ai",
        auth,
        max_time=300,
    )


def import_subject(acme, weyland):
    """Add subjects record for weyland in acme's environment"""
    subject = acme.subjects.import_subject(
        "weyland",
        weyland.subjects.read(SUBJECTS_SELF_ID),
    )

    # must wait for confirmation
    acme.subjects.wait_for_confirmation(subject["identity"])

    return subject


def create_example_access_policy(arch, label, subject):
    """Create access policy"""
    # consists of a filter selection entry and a selection criteria to restrict/redact
    # values of the asset attributes available to the sharee.

    # values pertaining to the access polcy itself.
    props = {
        "display_name": f"{label} access policy",
        "description": f"{label} Policy description",
    }

    # Filtering - access will be allowed to any asset that contains both these
    # attributes that equal these values. This happens to match the asset created
    # previously.
    filters = [
        {
            "or": [
                f"attributes.arc_display_type={label}_display_type",
            ]
        },
        {
            "or": [
                f"attributes.ext_vendor_name={label}",
            ]
        },
    ]

    # one must be the subject to gain access and only those fields
    # specified in include_attributes will be emitted.
    access_permissions = [
        {
            "subjects": [
                subject["identity"],
            ],
            "behaviours": ASSET_BEHAVIOURS,
            "include_attributes": [
                "arc_display_name",
            ],
        },
    ]

    return arch.access_policies.create(
        props,
        filters,
        access_permissions,
    )


def main():
    """Main function of share-asset."""
    # optional call to set the logger level for all subsystems. The argument can
    # be either "INFO" or "DEBUG". For more sophisticated logging control see the
    # documentation.
    set_logger("INFO")

    # For demonstration purposes we are going to assume that 2 organizations are
    # going to share an asset. The 2 organizations are ACME Corp and Weyland-Yutani
    # Corporation.
    acme = create_archivist("acme")
    weyland = create_archivist("weyland")

    # set a subject for weyland in acme's environment. The identity will be used as a
    # filter in the access permissions of the access_policy.
    weyland_subject_on_acme = import_subject(acme, weyland)
    print("weyland_subject on acme", json_dumps(weyland_subject_on_acme, indent=4))

    # acme creates an asset
    acme_asset = create_example_asset(acme, "acme")
    print("asset created in acme", json_dumps(acme_asset, indent=4))

    # now we want acme to share this asset to weyland via an access policy.
    access_policy = create_example_access_policy(acme, "acme", weyland_subject_on_acme)
    print("access policy created in acme", json_dumps(access_policy, indent=4))

    # display the asset as retrieved by weyland
    # NB: the attributes dict is redacted...
    weyland_asset = weyland.assets.read(acme_asset["identity"])
    print("asset read from weyland", json_dumps(weyland_asset, indent=4))

    # list matching access policies
    access_policies = list(
        acme.access_policies.list_matching_access_policies(acme_asset["identity"])
    )
    print("access policies read from acme", json_dumps(access_policies, indent=4))

    # delete all the access policies
    for access_policy in access_policies:
        acme.access_policies.delete(access_policy["identity"])

    # list matching access policies
    access_policies = list(
        acme.access_policies.list_matching_access_policies(acme_asset["identity"])
    )
    print("access policies read from acme", json_dumps(access_policies, indent=4))

    # display the asset as retrieved by the sharee
    # NB the asset is still shared even though there are no access policies
    weyland_asset = weyland.assets.read(acme_asset["identity"])
    print("asset read from weyland", json_dumps(weyland_asset, indent=4))

    acme.close()
    weyland.close()


if __name__ == "__main__":
    main()
