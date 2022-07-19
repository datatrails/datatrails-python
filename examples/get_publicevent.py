"""Get events of a public asset given url to event.

"""

from warnings import filterwarnings

from archivist.archivistpublic import ArchivistPublic

filterwarnings("ignore", message="Unverified HTTPS request")


def main():
    """Main function of getting public events."""
    # Initialize connection to ArchivistPublic
    public = ArchivistPublic()

    # URL is the fully-attested URL returned by archivist
    event = public.events.read(
        "https://app.rkvst.io/archivist/"
        "publicassets/87b1a84c-1c6f-442b-923e-a97516f4d275"
        "events/abcdef4c-1c6f-442b-923e-a97516f4d275"
    )
    print("event", event)


if __name__ == "__main__":
    main()
