"""Filter IAM subjects of a archivist connection given url to Archivist and user Token.

Main function parses in a url to the Archivist and credentials, which is a user authorization.
The main function would initialize an archivist connection using the url and
credentials, called "arch", then call arch.subjects.list() with suitable properties and
attributes.

"""
from os import getenv
from warnings import filterwarnings

from archivist.archivist import Archivist

filterwarnings("ignore", message="Unverified HTTPS request")


def main():
    """Main function of filtering subjects."""
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
        # count subjects...
        print("no.of subjects", arch.subjects.count(display_name="Some display name"))

        # iterate through the generator....
        for subject in arch.subjects.list(display_name="Some display name"):
            print("subject", subject)

        # alternatively one could pull the list for all subjects and cache locally...
        subjects = list(arch.subjects.list())
        for subject in subjects:
            print("subject", subject)


if __name__ == "__main__":
    main()
