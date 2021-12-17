"""Filter IAM access_policies of a archivist connection given url to Archivist
and user Token.

Main function parses in a url to the Archivist and client credentials , which is
a user authorization. The main function would initialize an archivist connection
using the url and the credentials, called "arch", then call arch.access_policies.list()
with suitable properties and attributes.

"""
from os import getenv

from archivist.archivist import Archivist


def main():
    """Main function of filtering access_policies."""

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

    # count access_policies...
    print(
        "no.of access_policies",
        arch.access_policies.count(display_name="Some display name"),
    )

    # iterate through the generator....
    for access_policy in arch.access_policies.list(display_name="Some display name"):
        print("access_policy", access_policy)

    # alternatively one could pull the list for all access policies and cache locally...
    access_policies = list(arch.access_policies.list())
    for access_policy in access_policies:
        print("access_policy", access_policy)


if __name__ == "__main__":
    main()
