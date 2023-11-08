"""Create a IAM subject given url to Archivist and user Token.

Main function parses in a url to the Archivist and credentials, which is a user
authorization. The main function would initialize an archivist connection using
the url and the credentials, called "arch".

'arch' is then called with arch.subjects.create_from_b64() and the subject will
be created.
"""
from os import getenv
from warnings import filterwarnings

from archivist.archivist import Archivist

filterwarnings("ignore", message="Unverified HTTPS request")


def main():
    """Main function of create subject.

    Parse in user input of url and credentials and use them to
    create an example archivist connection and create a subject.

    """
    # client id and client secret is obtained from the appidp endpoint - see the
    # application registrations example code in examples/applications_registration.py
    #
    # client id is an environment variable. client_secret is stored in a file in a
    # directory that has 0700 permissions. The location of this file is set in
    # the client_secret_file environment variable.
    client_id = getenv("DATATRAILS_APPREG_CLIENT")
    client_secret_file = getenv("DATATRAILS_APPREG_SECRET_FILENAME")
    with open(client_secret_file, mode="r", encoding="utf-8") as tokenfile:
        client_secret = tokenfile.read().strip()

    # Initialize connection to Archivist
    with Archivist(
        "https://app.datatrails.ai",
        (client_id, client_secret),
    ) as arch:
        # subject_string is the base64 encoding of the self subject of the other organization
        subject_string = (
            "eyJpZGVudGl0eSI6ICJzdWJqZWN0cy8wMDAwMDAwMC0wMDAwLTAwMDAtMDA"
            "wMC0wMDAwMDAwMDAwMDAiLCAiZGlzcGxheV9uYW1lIjogIlNlbGYiLCAid2"
            "FsbGV0X3B1Yl9rZXkiOiBbIjA0YzExNzNiZjc4NDRiZjFjNjA3Yjc5YzE4Z"
            "GIwOTFiOTU1OGZmZTU4MWJmMTMyYjhjZjNiMzc2NTcyMzBmYTMyMWEwODgw"
            "YjU0YTc5YTg4YjI4YmM3MTBlZGU2ZGNmM2Q4MjcyYzUyMTBiZmQ0MWVhODM"
            "xODhlMzg1ZDEyYzE4OWMiXSwgIndhbGxldF9hZGRyZXNzIjogWyIweDk5Rm"
            "E0QUFCMEFGMkI1M2YxNTgwODNEOGYyNDRiYjQ1MjMzODgxOTciXSwgInRlc"
            "3NlcmFfcHViX2tleSI6IFsiZWZkZzlKMFFoU0IyZzRJeEtjYVhnSm1OS2J6"
            "cHhzMDNGRllJaVlZdWVraz0iXSwgInRlbmFudCI6ICIiLCAiY29uZmlybWF"
            "0aW9uX3N0YXR1cyI6ICJDT05GSVJNQVRJT05fU1RBVFVTX1VOU1BFQ0lGSU"
            "VEIn0="
        )

        subject = arch.subjects.create_from_b64(
            {
                "display_name": "Some display name",
                "subject_string": subject_string,
            }
        )
        print("Subject", subject)


if __name__ == "__main__":
    main()
