"""compliance demo takes a yaml config file listing operations to be conducted serially.

It then runs the defined operations.
"""

import time
from enum import Enum
import argparse
import yaml

from archivist.archivist import Archivist
from archivist.errors import ArchivistError


class Operation(Enum):
    """
    Operation are the allowed archivist operations to be run.
    """

    CREATE_ASSET = 1
    CREATE_EVENT = 2
    CREATE_RICHNESS_COMPLIANCE_POLICY = 3
    CREATE_DYNAMIC_COMPLIANCE_POLICY = 4
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
            behaviours:
              - RecordEvidence
            attributes:
              radioactive: "true"
              radiation_level: "0"
              weight: "0"
    ```

    where:
     - `operation` is the operation to perform (see Operation Enum for options).
     - `to_print` is what to print to the console.
     - `wait_time` is time to wait before running the operation.
     - `asset_id` is the local reference to the asset, so can be referenced in other operations.
     - `behaviours` are a list of asset behaviours
     - `attributes are the asset's attributes

    please see example yaml files for other operation examples.

    To perform all the operations call the class instance.
    """

    assets = {}  # dict of assets created
    events = []  # list of events created
    policies = {}  # dict of policies created

    def __init__(self, url, token_file, config_file):

        with open(token_file, mode="r") as tokenfile:
            token = tokenfile.read().strip()

            self.client = Archivist(url, auth=token, verify=False)

        # read and save the config file
        yaml_stream = open(config_file, "r")
        self.yaml_object = yaml.load(yaml_stream, Loader=yaml.SafeLoader)

    def __call__(self):

        try:
            self.run_operations()

            # cleanup all policies
            print("Cleanup!")
            self.delete_all_policies()

        except (ArchivistError, KeyError):
            # always cleanup policies
            print("Cleanup!")
            self.delete_all_policies()

    def run_operations(self):
        """Runs all defined operations in self.yaml_object.
        """
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
            print("Waiting for {} seconds".format(wait_time))
            time.sleep(wait_time)

        # find an operation to run
        if operation == Operation.CREATE_ASSET.name:
            args.setdefault("behaviours", None)
            args.setdefault("attribute", None)

            self.create_asset(
                args["asset_id"],
                behaviours=args["behaviours"],
                attributes=args["attributes"]
            )

        if operation == Operation.CREATE_EVENT.name:
            args.setdefault("properties", None)
            args.setdefault("attributes", None)
            args.setdefault("asset_attributes", None)

            self.create_event(
                args["asset_id"],
                properties=args["properties"],
                attributes=args["attributes"],
                asset_attributes=args["asset_attributes"]
            )

        if operation == Operation.CREATE_RICHNESS_COMPLIANCE_POLICY.name:
            self.create_richness_compliance_policy(
                args["policy_id"],
                args["description"],
                args["display_name"],
                args["asset_filter"],
                args["richness_assertions"],
            )

        if operation == Operation.CREATE_DYNAMIC_COMPLIANCE_POLICY.name:
            self.create_dynamic_compliance_policy(
                args["policy_id"],
                args["description"],
                args["display_name"],
                args["asset_filter"],
                args["event_display_type"],
                args["closing_event_display_type"],
                args["dynamic_window"],
                args["dynamic_variability"]
            )

        if operation == Operation.CHECK_COMPLIANCE.name:
            self.check_compliance_policy(args["asset_id"])

        if operation == Operation.DELETE_COMPLIANCE.name:
            self.delete_compliance_policy(args["policy_id"])

        # new line at the end of every operation
        print("")

    def create_asset(self, asset_id, *, behaviours=None, attributes=None):
        """Creates an asset given its behaviours and attributes and adds it to the
           asset list.

            Args:
                asset_id (string): the unique local asset identity.
                behaviours (list): the behaviours associated with the asset
                attributes (dict): the attributes associated with the asset
        """

        if behaviours is None:
            behaviours = []

        if attributes is None:
            attributes = {}

        asset = self.client.assets.create(behaviours, attrs=attributes, confirm=True)
        print("Asset Created!")
        self.assets[asset_id] = asset

    def create_event(self, asset_id, *, properties=None, attributes=None, asset_attributes=None):
        """Creates an event for the given asset, based on its id.

            Args:
                asset_id (string): the unique local asset identity.
                properties (dict): the properties associated with the event
                attributes (dict): the attributes associated with the event
                asset_attributes (dict): the asset attributes associated with the event
        """

        if properties is None:
            properties = {}

        if attributes is None:
            attributes = {}

        if asset_attributes is None:
            asset_attributes = {}

        # find the asset identity
        asset_identity = self.assets[asset_id]["identity"]

        # create the event
        event = self.client.events.create(
            asset_identity,
            props=properties,
            attrs=attributes,
            asset_attrs=asset_attributes,
            confirm=True,
        )
        print("Event created!")

        self.events.append(event)

    def create_richness_compliance_policy(
        self,
        policy_id,
        description,
        display_name,
        asset_filter,
        richness_assertions,
    ):
        """Creates a richness compliance policy and adds it to the local policies.

            Args:
                policy_id (string): the unique local policy identity.
                description (string): the policy description
                display_name (string): the policy display name, non unique
                asset_filter (filter): in the form [{"or":["identity=foo",...],...}]
                richness_assertions (filter): format [{"or":["foo<7",...]}...]
        """

        policy = self.client.compliance_policies.create_richness(
            description,
            display_name,
            asset_filter,
            richness_assertions,
        )
        print("Policy Created!")

        self.policies[policy_id] = policy

    def create_dynamic_compliance_policy(
        self,
        policy_id,
        description,
        display_name,
        asset_filter,
        event_display_type,
        closing_event_display_type,
        dynamic_window,
        dynamic_variability,
    ):
        """Create dynamic tolerance compliance policy and adds it to the local policies

        Args:
            policy_id (string): the unique local policy identity.
            description (string): the policy description.
            display_name (string): the policy non-unique name.
            asset_filter (filter): in the form [{"or":["identity=foo",...],...}]
            event_display_type (string): target event display type
            closing_event_display_type (string): closing event display type.
            dynamic_window (int): valid period for policy
            dynamic_variability (float): % of stddevs allowed
        """

        policy = self.client.compliance_policies.create_dynamic_tolerance(
            description,
            display_name,
            asset_filter,
            event_display_type,
            closing_event_display_type,
            dynamic_window,
            dynamic_variability,
        )
        print("Policy Created!")

        self.policies[policy_id] = policy

    def check_compliance_policy(self, asset_id):
        """Checks an asset against all its applicable compliance policies.

            Args:
                asset_id (string): the unique local asset identity.
        """

        # find the asset identity
        asset_identity = self.assets[asset_id]["identity"]

        # check compliance
        compliance = self.client.compliance.read(asset_identity)
        print("Compliance: {}".format(compliance["compliant"]))

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
                "\tPolicy: {}. Reason: {}".format(
                    policy["display_name"], policy_outcome["reason"]
                )
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
