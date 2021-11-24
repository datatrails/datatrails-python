"""Filter events of a archivist connection given url to Archivist and user Token.

Main function parses in a url to the Archivist and a token, which is a user authorization.
The main function would initialize an archivist connection using the url and
the token, called "arch", then call arch.events.list() with appropriate properties and
attributes.
"""

from archivist.archivist import Archivist


def main():
    """Main function of filtering events.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and passed-in properties
    attributes to filter all events of the selected properties.

    """
    with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://app.rkvst.io",
        authtoken,
    )
    # Get all events with required attributes and properties
    props = {"confirmation_status": "CONFIRMED"}
    attrs = {"arc_display_type": "Traffic light"}
    for event in arch.events.list(asset_id="assets/-", props=props, attrs=attrs):
        print("event", event)

    # alternatively one could pull the list and cache locally...
    events = arch.events.list(asset_id="assets/-", props=props, attrs=attrs)
    for event in events:
        print("event", event)


if __name__ == "__main__":
    main()
