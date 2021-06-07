"""Filter IAM subjects of a archivist connection given url to Archivist and user Token.

Main function parses in a url to the Archivist and a token, which is a user authorization.
The main function would initialize an archivist connection using the url and
the token, called "arch", then call arch.subjects.list() with suitable properties and
attributes.

"""

from archivist.archivist import Archivist


def main():
    """Main function of filtering subjects."""
    with open(".auth_token", mode="r") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    arch = Archivist(
        "https://rkvst.poc.jitsuin.io",
        auth=authtoken,
    )

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
