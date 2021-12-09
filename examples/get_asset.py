"""Get an asset from a instance of Archivist

Main parses in a a url, which is an instance of Archivist and credentials, which
is a user authorization.

The main function would then call arch.assets.read_by_signature() to get one asset from
the instance.
"""
from os import getenv

from archivist.archivist import Archivist
from archivist.errors import ArchivistNotFoundError, ArchivistDuplicateError


def main():
    """Main function of get_asset.

    Parse in user input of url and credentials and use them to
    create an example archivist connection and fetch all assets.
    """
    # client id and client secret is obtained from the appidp endpoint - see the
    # application registrations example code in examples/applications_registration.py
    #
    # client id is an environment variable. client_scret is stored in a file in a
    # directory that has 0700 permissions. The location of this file is set in
    # the client_secret_file environment variable.
    client_id = getenv("ARCHIVIST_CLIENT_ID")
    client_secret_file = getenv("ARCHIVIST_CLIENT_SECRET_FILE")
    with open(client_secret_file, mode="r", encoding="utf-8") as tokenfile:
        client_secret = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://app.rkvst.io",
        (client_id, client_secret),
    )
    try:
        asset = arch.assets.read_by_signature(
            props={"tracked": "TRACKED"},
            attrs={"arc_display_type": "door"},
        )
    except (ArchivistNotFoundError, ArchivistDuplicateError) as ex:
        print("Unable to get asset", ex)

    else:
        print("Asset", asset["identity"])

    # alternatively get by identity
    asset = arch.assets.read(asset["identity"])
    print("Asset", asset["identity"])


if __name__ == "__main__":
    main()
