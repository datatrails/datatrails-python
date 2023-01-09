"""Filter assets of a archivist connection given url to Archivist and user Token.

Main function parses in a url to the Archivist and credentials, which is a user authorization.
The main function would initialize an archivist connection using the url and
the credentials, called "arch", then call arch.assets.list() with suitable properties and
attributes.

"""

from os import getenv
from warnings import filterwarnings

from archivist.archivist import Archivist

filterwarnings("ignore", message="Unverified HTTPS request")


def main():
    """Main function of filtering assets.

    Parse in user input of url and credentials and use them to
    create an example archivist connection and passed-in properties
    attributes to filter all assets of the selected properties and
    attributes through function get_matching_assets.
    """
    # client id and client secret is obtained from the appidp endpoint - see the
    # application registrations example code in examples/applications_registration.py
    #
    # client id is an environment variable. client_secret is stored in a file in a
    # directory that has 0700 permissions. The location of this file is set in
    # the client_secret_file environment variable.
    client_id = getenv("RKVST_APPREG_CLIENT")
    client_secret_file = getenv("RKVST_APPREG_SECRET_FILENAME")
    with open(client_secret_file, mode="r", encoding="utf-8") as tokenfile:
        client_secret = tokenfile.read().strip()

    # Initialize connection to Archivist
    with Archivist(
        "https://app.rkvst.io",
        (client_id, client_secret),
    ) as arch:

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
