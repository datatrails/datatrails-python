"""Create a IAM access_policy given url to Archivist and user Token.

Main function parses in
a url to the Archivist and client credentials, which is a user authorization.
The main function would initialize an archivist connection using the url and
the credentials, called "arch", then call arch.access_policies.create() and the access_policy
will be created.
"""

from os import getenv
from warnings import filterwarnings

from archivist.archivist import Archivist
from archivist.constants import ASSET_BEHAVIOURS

filterwarnings("ignore", message="Unverified HTTPS request")


def main():
    """Main function of create access_policy.

    Parse in user input of url and auth token and use them to
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

    with Archivist(
        "https://app.rkvst.io",
        (client_id, client_secret),
    ) as arch:

        props = {
            "display_name": "Friendly name of the policy",
            "description": "Description of the policy",
        }
        filters = [
            {
                "or": [
                    "attributes.arc_home_location_identity="
                    "locations/5ea815f0-4de1-4a84-9377-701e880fe8ae",
                    "attributes.arc_home_location_identity="
                    "locations/27eed70b-9e2b-4db1-b8c4-e36505350dcc",
                ]
            },
            {
                "or": [
                    "attributes.arc_display_type=Valve",
                    "attributes.arc_display_type=Pump",
                ]
            },
            {
                "or": [
                    "attributes.ext_vendor_name=SynsationIndustries",
                ]
            },
        ]
        access_permissions = [
            {
                "asset_attributes_read": ["toner_colour", "toner_type"],
                "asset_attributes_write": ["toner_colour"],
                "behaviours": ASSET_BEHAVIOURS,
                "event_arc_display_type_read": ["toner_type", "toner_colour"],
                "event_arc_display_type_write": ["toner_replacement"],
                "include_attributes": [
                    "arc_display_name",
                    "arc_display_type",
                    "arc_firmware_version",
                ],
                "subjects": [
                    "subjects/6a951b62-0a26-4c22-a886-1082297b063b",
                    "subjects/a24306e5-dc06-41ba-a7d6-2b6b3e1df48d",
                ],
                "user_attributes": [
                    {"or": ["group:maintainers", "group:supervisors"]},
                ],
            }
        ]
        access_policy = arch.access_policies.create(props, filters, access_permissions)
        print("access Policy", access_policy)


if __name__ == "__main__":
    main()
