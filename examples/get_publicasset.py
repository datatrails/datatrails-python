"""Get a public asset from a instance of Archivist

Main parses in a a url, which is an instance of Archivist.
"""

from archivist.archivist import Archivist


def main():
    """Main function of get_publicasset."""
    # Initialize connection to Archivist - no auth required
    arch = Archivist(
        "https://app.rkvst.io",
        None,
    )
    asset = arch.publicassets.read("assets/dc0dfc17-1d93-4b7a-8636-f740f40f7f52")
    print("Asset", asset)


if __name__ == "__main__":
    main()
