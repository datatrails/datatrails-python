"""Get a public asset from a instance of Archivist
"""

from warnings import filterwarnings

from archivist.archivistpublic import ArchivistPublic

filterwarnings("ignore", message="Unverified HTTPS request")


def main():
    """Main function of get_publicasset."""
    # Initialize connection to Archivist - no auth required
    public = ArchivistPublic()
    asset = public.assets.read(
        "https://app.rkvst.io/archivist/publicassets/dc0dfc17-1d93-4b7a-8636-f740f40f7f52"
    )
    print("Asset", asset)


if __name__ == "__main__":
    main()
