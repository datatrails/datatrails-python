"""Create a IAM subject given url to Archivist and user Token.

Main function parses in
a url to the Archivist and a token, which is a user authorization.
The main function would initialize an archivist connection using the url and
the token, called "arch", then call arch.subjects.create() and the subject will be created.
"""

from archivist.archivist import Archivist


def main():
    """Main function of create subject.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and create an asset.

    """
    with open(".auth_token", mode="r") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://app.rkvst.io",
        auth=authtoken,
    )

    subject = arch.subjects.create(
        "Some display name",
        ["walletkey1"],
        ["tesserakey1"],
    )
    print("Subject", subject)


if __name__ == "__main__":
    main()
