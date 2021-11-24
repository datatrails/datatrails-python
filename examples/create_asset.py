"""Create an asset given url to Archivist and user Token.

The module contains two functions: main and create_asset. Main function parses in
a url to the Archivist and a token, which is a user authorization.
The main function would initialize an archivist connection using the url and
the token, called "arch", then call arch.assets.create() and the asset will be created.
"""

from archivist.archivist import Archivist
from archivist.proof_mechanism import ProofMechanism


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
        "some_custom_attribute": "value"  # You can add any custom value as long as
        # it does not start with arc_
    }
    #
    # Select the mechanism used to prove evidence for the asset.  If the selected proof
    # mechanism is not enabled for your tenant then an error will occur.
    # If unspecified then SIMPLE_HASH is used.
    # proof_mechanism = ProofMechanism.KHIPU.name
    props = {
        "proof_mechanism": ProofMechanism.KHIPU.name,
    }

    # The first argument are the properties of the asset
    # The second argument are the attributes of the asset
    # The third argument is wait for confirmation:
    #   If @confirm@ is True then this function will not
    #   return until the asset is confirmed on the blockchain and ready
    #   to accept events (or an error occurs)
    #
    return arch.assets.create(props=props, attrs=attrs, confirm=True)
    # alternatively if some work can be done whilst the asset is confirmed then this call can be
    # replaced by a two-step alternative:

    # asset = arch.assets.create(props=props, attrs=attrs, confirm=False)

    # ... do something else here
    # and then wait for confirmation

    # self.arch.assets.wait_for_confirmation(asset['identity']))


def main():
    """Main function of create asset.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and create an asset.

    """
    with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist. max_time is the time to wait for confirmation
    # of an asset or event creation - the default is 1200 seconds but one can optionally
    # specify a different value here particularly when creating assets on SIMPLE_HASH
    # (rather than KHIPU) as confirmation times are much shorter in this case.
    arch = Archivist(
        "https://app.rkvst.io",
        authtoken,
        max_time=300,
    )
    # Create a new asset
    asset = create_asset(arch)
    print("Asset", asset)


if __name__ == "__main__":
    main()
