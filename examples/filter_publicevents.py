"""Filter events of a public asset given url to asset.

"""

from archivist.archivistpublic import ArchivistPublic


def main():
    """Main function of filtering public events.

    Parse in user input of url.
    create an example archivist connection and passed-in properties
    attributes to filter all events of the selected properties.

    """
    # Initialize connection to ArchivistPublic
    with ArchivistPublic() as public:
        # Get all public events with required attributes and properties
        props = {"confirmation_status": "CONFIRMED"}
        attrs = {"arc_display_type": "Traffic light"}

        for event in public.events.list(
            asset_id=(
                "https://app.datatrails.ai/archivist/"
                "publicassets/87b1a84c-1c6f-442b-923e-a97516f4d275"
            ),
            props=props,
            attrs=attrs,
        ):
            print("event", event)


if __name__ == "__main__":
    main()
