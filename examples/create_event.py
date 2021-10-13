"""Create an event for an asset given url to Archivist and user Token.

The module contains four functions: main, create_asset and create_event.
Main function parses in a url to the Archivist and a token, which is a user authorization.
The main function would initialize an archivist connection using the url and
the token, called "arch", then call create_assets and pass in "arch" and
create_assets will build create_asset, which is a archivist connection function
to create a new asset for the archivist through archivist connection. The main funciton then
calls create_event and pass in "arch" and the created asset to create a new event for the asset.
"""

from archivist.archivist import Archivist


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

    return arch.events.create(asset["identity"], props=props, attrs=attrs, confirm=True)
    # alternatively if some work can be done whilst the event is confirmed then this call can be
    # replaced by a two-step alternative:

    # event = arch.events.create(asset["identity"], props=props, attrs=attrs, confirm=False)

    # ... do something else here
    # and then wait for confirmation

    # self.arch.events.wait_for_confirmation(event['identity'])


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
    # The first argument is the attributes of the asset
    # The second argument is wait for confirmation:
    #   If @confirm@ is True then this function will not
    #   return until the asset is confirmed on the blockchain and ready
    #   to accept events (or an error occurs)
    #   After an asset is submitted to the blockchain (submitted),
    #   it will be in the "Pending" status.
    #   Once it is added to the blockchain, the status will be changed to "Confirmed"
    return arch.assets.create(attrs=attrs, confirm=True)


def main():
    """Main function of create event.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and create an asset.
    The main function then uses the asset to create an event for
    the asset and fetch the event.

    """
    with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://app.rkvst.io",
        auth=authtoken,
    )
    # Create a new asset
    asset = create_asset(arch)
    # Create a new event
    event = create_event(arch, asset)
    # Fetch the event
    event = arch.events.read(event["identity"])
    print("Event", event)


if __name__ == "__main__":
    main()
