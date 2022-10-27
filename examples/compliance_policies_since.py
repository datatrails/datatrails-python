"""Define a compliance policy that alerts when an asset has expired.

Main function parses in a url to the Archivist and client credentials , which is
a user authorization. The main function would initialize an archivist connection
using the url and the credentials, called "arch", then call arch.access_policies.list()
with suitable properties and attributes.

"""
from json import dumps as json_dumps
from os import getenv
from time import sleep
from uuid import uuid4
from warnings import filterwarnings

from archivist.archivist import Archivist
from archivist.compliance_policy_requests import (
    CompliancePolicySince,
)
from archivist.utils import get_auth

filterwarnings("ignore", message="Unverified HTTPS request")


def get_archivist():
    """Create Archivist endpoint."""

    # client id and client secret is obtained from the appidp endpoint - see the
    # application registrations example code in examples/applications_registration.py
    #
    # client id is an environment variable. client_secret is stored in a file in a
    # directory that has 0700 permissions. The location of this file is set in
    # the client_secret_file environment variable.
    #
    auth = get_auth(
        auth_token=getenv("ARCHIVIST_AUTHTOKEN"),
        auth_token_filename=getenv("ARCHIVIST_AUTHTOKEN_FILENAME"),
        client_id=getenv("ARCHIVIST_CLIENT_ID"),
        client_secret=getenv("ARCHIVIST_CLIENT_SECRET"),
        client_secret_filename=getenv("ARCHIVIST_CLIENT_SECRET_FILENAME"),
    )

    # Initialize connection to Archivist
    arch = Archivist(
        "https://app.rkvst.io",
        auth,
    )
    return arch


def create_compliance_policy(arch, tag):
    """Compliance policy which expires 10 seconds after a
    Maintenance Performed event on a 'Traffic Light' has occurred.

    Usually the expiry time is on the order of days or weeks..

    Additionally the use of tag is simply to make this example
    repeatable.
    """
    compliance_policy = arch.compliance_policies.create(
        CompliancePolicySince(
            description="Maintenance should be performed every 10 seconds",
            display_name="Regular Maintenance of Traffic light",
            asset_filter=[
                ["attributes.arc_display_type=Traffic Light"],
            ],
            event_display_type=f"Maintenance Performed {tag}",
            time_period_seconds=10,  # very short so we can test
        )
    )
    print("SINCE_POLICY:", json_dumps(compliance_policy, indent=4))
    return compliance_policy


def create_traffic_light(arch):
    """
    Creates a traffic light.

    Note that arc_display_type siginfies a Traffic Light
    """

    traffic_light = arch.assets.create(
        attrs={
            "arc_display_name": "Traffic light model 54",
            "arc_description": "Traffic flow control light at A603 North East",
            "arc_display_type": "Traffic Light",
        },
        confirm=True,
    )
    print("TRAFFIC_LIGHT:", json_dumps(traffic_light, indent=4))
    return traffic_light


def perform_maintenance(arch, traffic_light, tag):
    """
    Perform maintenance on traffic light
    """
    maintenance_performed = arch.events.create(
        traffic_light["identity"],
        {
            "operation": "Record",
            "behaviour": "RecordEvidence",
        },
        {
            "arc_description": "Maintenance performed on traffic light",
            "arc_display_type": f"Maintenance Performed {tag}",
        },
        confirm=True,
    )
    print("MAINTENANCE_PERFORMED:", json_dumps(maintenance_performed, indent=4))


def main():
    """
    Connect to archivist, create an asset, create a compliance policy
    execute an event on the asset and check if the asset has expired
    """
    # first get Archivist connection.
    arch = get_archivist()

    tag = uuid4()  # make this example repeatable

    # make a SINCE compliance policy that alerts when the
    # maintenance performed event has expired.
    compliance_policy = create_compliance_policy(arch, tag)

    # create an asset that matches the assets_filter field in the
    # compliance policy.
    traffic_light = create_traffic_light(arch)

    # perform maintenance on the asset which is valid for 10 seconds.
    perform_maintenance(arch, traffic_light, tag)

    # and check compliance - should be OK.
    print("Sleep 1 second...")
    sleep(1)
    compliance = arch.compliance.compliant_at(
        traffic_light["identity"],
    )
    print("COMPLIANCE (true):", json_dumps(compliance, indent=4))

    # however waiting long enough (> 10s) will cause the asset to
    # become non-compliant...
    print("Sleep 15 seconds...")
    sleep(15)
    compliance = arch.compliance.compliant_at(
        traffic_light["identity"],
    )
    print("COMPLIANCE (false):", json_dumps(compliance, indent=4))

    # finally delete the compliance_policy
    arch.compliance_policies.delete(
        compliance_policy["identity"],
    )
    arch.close()


if __name__ == "__main__":
    main()
