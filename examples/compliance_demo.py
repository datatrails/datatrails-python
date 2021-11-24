"""compliance demo takes a yaml config file listing operations to be conducted serially.

It then runs the defined operations.
"""

import argparse
from enum import Enum
import time
import warnings
import yaml

from archivist.archivist import Archivist
from archivist.errors import ArchivistError
from archivist.compliance_policy_requests import (
    CompliancePolicyDynamicTolerance,
    CompliancePolicyRichness,
)

warnings.filterwarnings("ignore", message="Unverified HTTPS request")


class Operation(Enum):
    """
    Operation are the allowed archivist operations to be run.
    """

    CREATE_ASSET = 1
    CREATE_EVENT = 2
    CREATE_COMPLIANCE_POLICY_RICHNESS = 3
    CREATE_COMPLIANCE_POLICY_DYNAMIC_TOLERANCE = 4
    CHECK_COMPLIANCE = 5
    DELETE_COMPLIANCE = 6


class ArchivistStoryRunner:
    """
    ArchivistStoryRunner takes a url, token_file and a yaml config_file.

    The yaml config_file contains a list of `operations` to be performed serially, e.g.

    ```
    operations:

        - operation: CREATE_ASSET
            to_print: Create an empty radiation bag with id 1.
            wait_time: 10
            asset_id: radiation bag 1
            args:
              attrs:
                radioactive: "true"
                radiation_level: "0"
                weight: "0"
    ```

    where:
     - `operation` is the operation to perform (see Operation Enum for options).
     - `to_print` is what to print to the console.
     - `wait_time` is time to wait before running the operation.
     - `asset_id` is the local reference to the asset, so can be referenced in other operations.
     - `attrs are the asset's attributes

    please see example yaml files for other operation examples.

    To perform all the operations call the class instance.
    """

    assets = {}  # dict of assets created
    events = []  # list of events created
    policies = {}  # dict of policies created

    def __init__(self, url, token_file, config_file):

        with open(token_file, mode="r", encoding="utf-8") as tokenfile:
            token = tokenfile.read().strip()

            self.client = Archivist(url, token, verify=False)

        # read and save the config file
        with open(config_file, "r", encoding="utf-8") as y:
            self.yaml_object = yaml.load(y, Loader=yaml.SafeLoader)

    def __call__(self):

        try:
            self.run_operations()
        except (ArchivistError, KeyError) as ex:
            print("exception", ex)
        finally:
            print("Cleanup!")
            self.delete_all_policies()

    def run_operations(self):
        """Runs all defined operations in self.yaml_object."""
        for operation in self.yaml_object["operations"]:
            operation.setdefault("wait_time", 0)
            operation.setdefault("to_print", None)

            self.run_operation(
                operation["operation"],
                operation,
                to_print=operation["to_print"],
                wait_time=operation["wait_time"],
            )

    def run_operation(self, operation, args, *, to_print=None, wait_time=0):
        """Runs an operation given parameters and the type of operation.

        Args:
            operation (string): the type of operation to run.
            args (dict): the operation arguments.
            to_print (string): string to print to console.
            wait_time (int): the time to wait before running the operation
        """

        # print out the story of the operation
        if to_print is not None:
            print(to_print)

        # wait for a number of seconds
        if wait_time > 0:
            print("Waiting for", wait_time, " seconds")
            time.sleep(wait_time)

        # find an operation to run
        if operation == Operation.CREATE_ASSET.name:
            asset_id = args["args"]["attrs"]["arc_description"]
            asset = self.client.assets.create(**args["args"])
            self.assets[asset_id] = asset
            print("Asset Created", asset_id)
            return

        if operation == Operation.CREATE_EVENT.name:
            asset_id = args["asset_id"]
            asset_identity = self.assets[asset_id]["identity"]
            event = self.client.events.create(
                asset_identity,
                **args["args"],
            )
            self.events.append(event)
            print("Asset", asset_id, "event created", event["identity"])
            return

        if operation == Operation.CREATE_COMPLIANCE_POLICY_RICHNESS.name:
            policy_id = args["policy_id"]
            policy = self.client.compliance_policies.create(
                CompliancePolicyRichness(**args["args"]),
            )
            print("Policy Created", policy_id)

            self.policies[policy_id] = policy
            return

        if operation == Operation.CREATE_COMPLIANCE_POLICY_DYNAMIC_TOLERANCE.name:
            policy_id = args["policy_id"]
            policy = self.client.compliance_policies.create(
                CompliancePolicyDynamicTolerance(**args["args"]),
            )
            print("Policy Created", policy_id)

            self.policies[policy_id] = policy
            return

        if operation == Operation.CHECK_COMPLIANCE.name:
            self.check_compliance_policy(args["asset_id"])
            return

        if operation == Operation.DELETE_COMPLIANCE.name:
            self.delete_compliance_policy(args["policy_id"])
            return

        # new line at the end of every operation
        print("Illegal operation", operation)

    def check_compliance_policy(self, asset_id):
        """Checks an asset against all its applicable compliance policies.

        Args:
            asset_id (string): the unique local asset identity.
        """

        # find the asset identity
        asset_identity = self.assets[asset_id]["identity"]

        # check compliance
        compliance = self.client.compliance.compliant_at(asset_identity)
        print("Compliance: ", compliance["compliant"])

        # if there is a reason print it
        for policy_outcome in compliance["compliance"]:

            if policy_outcome["reason"] == "":
                continue

            # get the compliance policy
            policy = self.client.compliance_policies.read(
                policy_outcome["compliance_policy_identity"]
            )

            # print the policy name and the reason
            print(
                "\tPolicy: ",
                policy["display_name"],
                ": Reason: ",
                policy_outcome["reason"],
            )

    def delete_compliance_policy(self, policy_id):
        """Delete a compliance policy, given its local id.

        Args:
            policy_id (string): the unique local policy identity.
        """

        # find the asset identity
        policy_identity = self.policies[policy_id]["identity"]

        # delete the policy
        self.client.compliance_policies.delete(policy_identity)
        print("Policy Deleted!")

    def delete_all_policies(self):
        """
        delete_all_policies deletes all compliance policies that were created.
        """

        for policy_id in self.policies:
            self.delete_compliance_policy(policy_id)


def main():
    """
    main creates a ArchivistStoryRunner and runs all the operations defined
      in the given yaml file.
    """
    # create the argparser
    parser = argparse.ArgumentParser()

    parser.add_argument("url", help="the archivist url.")
    parser.add_argument("tokenfile", help="the auth token file location.")
    parser.add_argument(
        "yamlfile", help="the yaml file describing the operations to conduct"
    )

    args = parser.parse_args()

    runner = ArchivistStoryRunner(args.url, args.tokenfile, args.yamlfile)
    runner()


if __name__ == "__main__":
    main()
