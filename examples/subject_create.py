"""Create a IAM subject given url to Archivist and user Token.

Main function parses in
a url to the Archivist and credentials, which is a user authorization.
The main function would initialize an archivist connection using the url and
the credentials, called "arch", then call arch.subjects.create() and the subject will be created.
"""
from os import getenv

from archivist.archivist import Archivist


def main():
    """Main function of create subject.

    Parse in user input of url and credentials and use them to
    create an example archivist connection and create an asset.

    """
    # client id and client secret is obtained from the appidp endpoint - see the
    # application registrations example code in examples/applications_registration.py
    #
    # client id is an environment variable. client_secret is stored in a file in a
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

    subject = arch.subjects.create(
        "Some display name",
        ["walletkey1"],
        ["tesserakey1"],
    )
    print("Subject", subject)


if __name__ == "__main__":
    main()
