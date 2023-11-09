"""Create a IAM application registration from a  given url to Archivist and user Token.

Main function parses in
a url to the Archivist and a token, which is a user authorization.
The main function would initialize an archivist connection using the url and
the token, called "arch", then call arch.applications.create() and the application will be created.

Create JWT token after updating, regenerating secrets.
"""

from json import dumps as json_dumps
from uuid import uuid4
from warnings import filterwarnings

from archivist.archivist import Archivist
from archivist.proof_mechanism import ProofMechanism

filterwarnings("ignore", message="Unverified HTTPS request")


def main():
    """Main function of create subject.

    Parse in user input of url and auth token and use them to
    create an example archivist connection and create an application registration.

    """
    with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
        authtoken = tokenfile.read().strip()

    # Initialize connection to Archivist
    with Archivist(
        "https://app.datatrails.ai",
        authtoken,
    ) as arch:
        # create application
        application = arch.applications.create(
            f"Application display name {uuid4()}",
            {
                "serial_number": "TL1000000101",
                "has_cyclist_light": "true",
            },
        )
        print("create application", json_dumps(application, indent=4))

        # convert to token
        appidp = arch.appidp.token(
            application["client_id"],
            application["credentials"][0]["secret"],
        )
        print("appidp", json_dumps(appidp, indent=4))

        # regenerate secrets
        application = arch.applications.regenerate(
            application["identity"],
        )
        print("regenerate application", json_dumps(application, indent=4))

        # convert to token
        appidp = arch.appidp.token(
            application["client_id"],
            application["credentials"][0]["secret"],
        )
        print("appidp", json_dumps(appidp, indent=4))

        # update application
        application = arch.applications.update(
            application["identity"],
            custom_claims={
                "serial_number": "TL2000000202",
                "has_cyclist_light": "false",
            },
        )
        print("update application", json_dumps(application, indent=4))

        # convert to token
        appidp = arch.appidp.token(
            application["client_id"],
            application["credentials"][0]["secret"],
        )
        print("appidp", json_dumps(appidp, indent=4))

        # regenerate secrets
        application = arch.applications.regenerate(
            application["identity"],
        )
        print("regenerate application", json_dumps(application, indent=4))

        # convert to token
        appidp = arch.appidp.token(
            application["client_id"],
            application["credentials"][0]["secret"],
        )
        print("appidp", json_dumps(appidp, indent=4))

        # now create Archivist with automatically refreshed jwt token
        # this archivist does not allow app registrations.
        with Archivist(
            "https://app.datatrails.ai",
            (application["client_id"], application["credentials"][0]["secret"]),
        ) as arch1:
            # create an asset
            asset = arch1.assets.create(
                props={
                    "proof_mechanism": ProofMechanism.SIMPLE_HASH.name,
                },
                attrs={
                    "arc_display_name": "display_name",
                    "arc_description": "display_description",
                    "arc_display_type": "desplay_type",
                    "some_custom_attribute": "value",
                },
                confirm=True,
            )
            print("asset", json_dumps(asset, indent=4))

            # delete application
            application = arch.applications.delete(
                application["identity"],
            )


if __name__ == "__main__":
    main()
