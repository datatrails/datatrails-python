"""Filter assets of a archivist connection given url to Archivist and user Token.

Main function parses in a url to the Archivist and a token, which is a user authorization.
The main function would initialize an archivist connection using the url and
the token, called "arch", then call arch.assets.list() with suitable properties and
attributes.

"""

from archivist.archivist import Archivist


def main():
    """Main function of filtering assets.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and passed-in properties
    attributes to filter all assets of the selected properties and
    attributes through function get_matching_assets.
    """
    with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://app.rkvst.io",
        auth=authtoken,
    )

    # list all assets with required attributes and properties
    props = {"confirmation_status": "CONFIRMED"}
    attrs = {"arc_display_type": "Traffic light"}

    # iterate through the generator....
    for asset in arch.assets.list(props=props, attrs=attrs):
        print("asset", asset)

    # alternatively one could pull the list and cache locally...
    assets = list(arch.assets.list(props=props, attrs=attrs))
    for asset in assets:
        print("asset", asset)


if __name__ == "__main__":
    main()
