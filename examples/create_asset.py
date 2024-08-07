"""Create an asset given url to Archivist and user Token.

The module contains two functions: main and create_asset. Main function parses in
a url to the Archivist and credentials, which is a user authorization.
The main function would initialize an archivist connection using the url and
the credentials, called "arch", then call arch.assets.create() and the asset will be created.
"""

from os import getenv
from warnings import filterwarnings

from archivist.archivist import Archivist
from archivist.logger import set_logger
from archivist.utils import get_auth

filterwarnings("ignore", message="Unverified HTTPS request")


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
    #
    # Optionally one can create a publicasset by specifying public as True
    # If unspecified a private asset wll be created.
    props = {
        "public": True,
    }

    # The first argument are the properties of the asset
    # The second argument are the attributes of the asset
    # The third argument is wait for confirmation:
    #   If @confirm@ is True then this function will not
    #   return until the asset is confirmed.
    #
    return arch.assets.create(props=props, attrs=attrs, confirm=True)
    # alternatively if some work can be done whilst the asset is confirmed then this call can be
    # replaced by a two-step alternative:

    # asset = arch.assets.create(props=props, attrs=attrs)

    # ... do something else here
    # and then wait for confirmation

    # self.arch.assets.wait_for_confirmation(asset['identity']))


def main():
    """Main function of create asset.

    Parse in user input of url and client id/secrets and use them to
    create an example archivist connection and create an asset.

    """
    # optional call to set the logger level for all subsystems. The argument can
    # be either "INFO" or "DEBUG". For more sophisticated logging control see the
    # documentation.
    set_logger("INFO")

    # client id and client secret is obtained from the appidp endpoint - see the
    # application registrations example code in examples/applications_registration.py
    #
    # client id is an environment variable. client_secret is stored in a file in a
    # directory that has 0700 permissions. The location of this file is set in
    # the client_secret_file environment variable.
    auth = get_auth(
        auth_token=getenv("DATATRAILS_AUTHTOKEN"),
        auth_token_filename=getenv("DATATRAILS_AUTHTOKEN_FILENAME"),
        client_id=getenv("DATATRAILS_APPREG_CLIENT"),
        client_secret=getenv("DATATRAILS_APPREG_SECRET"),
        client_secret_filename=getenv("DATATRAILS_APPREG_SECRET_FILENAME"),
    )

    # Initialize connection to Archivist. max_time is the time to wait for confirmation
    # of an asset or event creation - the default is 30 seconds but one can optionally
    # specify a different value.
    # Confirmation guarantees that 3rd parties can retrieve and cryptographically
    # verify your Events, which can take a few seconds to propagate. It is typically
    # not necessary to wait unless your workflow involves near-real-time
    # communication with 3rd parties and the 3rd party needs instant cryptographic
    # verification of your new Asset.

    # The optional partner id field is allocated by Datatrails to partners - partners are then
    # expected to specify this value when submitting any request to the archivist product.
    # Leave blank if if you do not have a partner ID.
    with Archivist(
        "https://app.datatrails.ai",
        auth,
        max_time=300,
        partner_id="acme/f7a6beef-f01c-4b39-a494-3fa6b45d6bf4",
    ) as arch:
        # Create a new asset
        asset = create_asset(arch)
        print("Asset", asset)


if __name__ == "__main__":
    main()
