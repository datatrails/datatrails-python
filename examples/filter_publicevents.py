"""Filter events of a archivist connection given url to Archivist.

Main function parses in a url to the Archivist.
The main function would initialize an archivist connection using the url and
called "arch", then call arch.publicevents.list() with appropriate properties and
attributes.
"""

from archivist.archivist import Archivist


def main():
    """Main function of filtering events.

    Parse in user input of url.
    create an example archivist connection and passed-in properties
    attributes to filter all events of the selected properties.

    """
    # Initialize connection to Archivist
    arch = Archivist(
        "https://app.rkvst.io",
        None,
    )
    # Get all events with required attributes and properties
    props = {"confirmation_status": "CONFIRMED"}
    attrs = {"arc_display_type": "Traffic light"}
    for event in arch.publicevents.list(props=props, attrs=attrs):
        print("event", event)

    # alternatively one could pull the list and cache locally...
    events = arch.publicevents.list(props=props, attrs=attrs)
    for event in events:
        print("event", event)


if __name__ == "__main__":
    main()
