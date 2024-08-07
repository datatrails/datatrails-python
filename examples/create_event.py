"""Create an event for an asset given url to Archivist and user Token.

The module contains four functions: main, create_asset, create_event and
get_verified_domain.

The main function would initialize an archivist connection using the url and
the credentials, called "arch".

create_asset will execute 'assets.create', which is a archivist connection function
to create a new asset for the archivist through archivist connection. The main funciton then
calls create_event and pass in "arch" and the created asset to create a new event for the asset.

In both cases the verified domain name is displayed.
"""

from json import dumps as json_dumps
from os import getenv
from warnings import filterwarnings

from archivist.archivist import Archivist
from archivist.logger import set_logger

filterwarnings("ignore", message="Unverified HTTPS request")


def get_verified_domain(arch, identity):
    """Get the verified domain for the tenant.

    Args:
        arch: archivist connection.
        identity: an identity of a tenant

    Returns:
        verified_domain: name of the verified domain
                         for the asset.

    """

    tenancy = arch.tenancies.publicinfo(identity)
    return tenancy.get("verified_domain", "")


def create_event(arch, asset):
    """Create an event for the passed-in asset.

    Args:
        arch: archivist connection.
        asset: an asset created using aconn

    Returns:
        new_event: a new event for the asset.

    """

    # props can be defined for different behaviours and the attributes associated with
    # different behaviours are also different.
    props = {
        "operation": "Record",
        # This event is used to record evidence.
        "behaviour": "RecordEvidence",
        # Optional Client-claimed time at which the maintenance was performed
        "timestamp_declared": "2019-11-27T14:44:19Z",
        # Optional Client-claimed identity of person performing the operation
        "principal_declared": {
            "issuer": "idp.synsation.io/1234",
            "subject": "phil.b",
            "email": "phil.b@synsation.io",
        },
    }
    attrs = {
        # Required Details of the RecordEvidence request
        "arc_description": "Safety conformance approved for version 1.6.",
        # Required The evidence to be retained in the asset history
        "arc_evidence": "DVA Conformance Report attached",
        # Example Client can add any additional information in further attributes,
        # including free text or attachments
        "conformance_report": "blobs/e2a1d16c-03cd-45a1-8cd0-690831df1273",
    }
    #
    # There are 3 alternatives
    #
    # 1. Create the event:
    return arch.events.create(asset["identity"], props=props, attrs=attrs)
    #
    # 2. alternatively one can wait for the asset to be confirmed in the
    #    immutable store.
    #    The second argument is wait for confirmation:
    #      If @confirm@ is True then this function will not
    #      return until the asset is confirmed.
    #
    # Confirmation guarantees that 3rd parties can retrieve and cryptographically
    # verify your Events, which can take a few seconds to propagate. It is typically
    # not necessary to wait unless your workflow involves near-real-time
    # communication with 3rd parties and the 3rd party needs instant cryptographic
    # verification of your new Asset.
    # return arch.events.create(asset["identity"], props=props, attrs=attrs, confirm=True)
    #
    # 3. lastly if some work can be done whilst the asset is confirmed then this call
    # can be replaced by a two-step alternative:

    # event = arch.events.create(asset["identity"], props=props, attrs=attrs)

    # ... do something else here
    # and then wait for confirmation

    # return arch.events.wait_for_confirmation(event["identity"])


def create_asset(arch):
    """Create an asset using Archivist Connection.

    Args:
        arch: archivist connection.

    Returns:
        newasset: a new asset created.

    """
    attrs = {
        "arc_display_name": "display_name",  # Asset's display name in the user interface
        "arc_description": "display_description",  # Asset's description in the user interface
        "arc_display_type": "desplay_type",  # Arc_display_type is a free text field
        # allowing the creator of
        # an asset to specify the asset
        # type or class. Be careful when setting this:
        # assets are grouped by type and
        # sharing policies can be
        # configured to share assets based on
        # their arc_display_type.
        # So a mistake here can result in asset data being
        # under- or over-shared.
        "some_custom_attribute": "value",  # You can add any custom value as long as
        # it does not start with arc_
    }
    # The first argument is the attributes of the asset
    return arch.assets.create(attrs=attrs)


def main():
    """Main function of create event.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and create an asset.
    The main function then uses the asset to create an event for
    the asset and fetch the event.

    """
    # optional call to set the logger level for all subsystems. The argumant can
    # be either "INFO" or "DEBUG". For more sophisticated logging control see the
    # documentation.
    set_logger("DEBUG")

    # client id and client secret is obtained from the appidp endpoint - see the
    # application registrations example code in examples/applications_registration.py
    #
    # client id is an environment variable. client_secret is stored in a file in a
    # directory that has 0700 permissions. The location of this file is set in
    # the client_secret_file environment variable.
    client_id = getenv("DATATRAILS_APPREG_CLIENT")
    client_secret_file = getenv("DATATRAILS_APPREG_SECRET_FILENAME")
    with open(client_secret_file, mode="r", encoding="utf-8") as tokenfile:
        client_secret = tokenfile.read().strip()

    # Initialize connection to Archivist
    with Archivist(
        "https://app.datatrails.ai",
        (client_id, client_secret),
    ) as arch:
        # Create a new asset
        asset = create_asset(arch)
        print("Asset", json_dumps(asset, sort_keys=True, indent=4))
        print(
            "Verified domain '",
            get_verified_domain(arch, asset["tenant_identity"]),
            "'",
        )

        # Create a new event
        event = create_event(arch, asset)
        print("Event", json_dumps(event, sort_keys=True, indent=4))
        print(
            "Verified domain '",
            get_verified_domain(arch, event["tenant_identity"]),
            "'",
        )

        # Fetch the event
        event = arch.events.read(event["identity"])
        print("Event", json_dumps(event, sort_keys=True, indent=4))
        print(
            "Verified domain '",
            get_verified_domain(arch, event["tenant_identity"]),
            "'",
        )


if __name__ == "__main__":
    main()
