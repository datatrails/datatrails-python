"""Get an asset from a instance of Archivist

Main parses in a a url, which is an instance of Archivist and a token, which
is a user authorization.

The main function would then call arch.assets.read_by_signature() to get one asset from
the instance.
"""


from archivist.archivist import Archivist
from archivist.errors import ArchivistNotFoundError, ArchivistDuplicateError


def main():
    """Main function of get_asset.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and fetch all assets.
    """
    with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://app.rkvst.io",
        auth=authtoken,
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
