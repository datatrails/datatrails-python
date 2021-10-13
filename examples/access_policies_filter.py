"""Filter IAM access_policies of a archivist connection given url to Archivist and user Token.

Main function parses in a url to the Archivist and a token, which is a user authorization.
The main function would initialize an archivist connection using the url and
the token, called "arch", then call arch.access_policies.list() with suitable properties and
attributes.

"""

from archivist.archivist import Archivist


def main():
    """Main function of filtering access_policies."""
    with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://app.rkvst.io",
        auth=authtoken,
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
