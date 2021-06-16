"""archivist story runner takes a yaml config file listing operations to be conducted serially.

It then runs the defined operations.
"""

from archivist.compliance_polices import PolicyType
from archivist.archivist import Archivist

# remove warning from console
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
from enum import Enum
import yaml
import argparse


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Operation(Enum):
    """
    Operation are the allowed archivist operations to be run.
    """

    CREATE_ASSET = 1
    CREATE_EVENT = 2
    CREATE_COMPLIANCE_POLICY = 3
    CHECK_COMPLIANCE = 4
    DELETE_COMPLIANCE = 5

def parse_arg(arg, key, default=None):
    """
    parse_arg parses a dictionary arg, and returns the value of a key.
              if the key doesn't exist within the dictionary the default is returned.
              if the default is None, then KeyError is raised.
    """
    try:
        return arg[key]
    except KeyError as ke:
        if default == None:
            raise ke

        return default

class ArchivistStoryRunner():
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

    To perform all the operations call the `run` method.
    """

    assets = dict()  # dict of assets created
    events = list()  # list of events created
    policies = dict()  # dict of policies created

    def __init__(self, url, token_file, config_file):
        """
        constructor
        :param url: the url of the archivist instance.
        :param token_file: the token auth for the archivist instance.
        :param config_file: the yaml config file listing all the operations to perform.
        """

        with open(token_file, mode="r") as tokenfile:
            token = tokenfile.read().strip()

            self.client = Archivist(url, auth=token, verify=False)

        # read and save the config file
        yaml_stream = open(config_file, 'r')
        self.yaml_object = yaml.load(yaml_stream, Loader=yaml.SafeLoader)

    def run(self):
        """
        run runs all operations defined in self.yaml_object
        """
        for operation in self.yaml_object["operations"]:
            wait_time = parse_arg(operation, "wait_time", 0)
            to_print = parse_arg(operation, "to_print", "")

            self.run_operation(operation["operation"], operation, to_print=to_print, wait_time=wait_time)

        # cleanup all policies
        print("Cleanup!")
        self.delete_all_policies()

    def run_operation(self, operation, operation_args, to_print="", wait_time=0):
        """
        run_operation runs an operation based on the given Operation enum.
        """

        # print out the story of the operation
        if to_print != "":
            print(to_print)

        # wait for a number of seconds
        if wait_time > 0:
            print("Waiting for {} seconds".format(wait_time))
            time.sleep(wait_time)

        # find an operation to run
        if operation == Operation.CREATE_ASSET.name:
            self.create_asset(operation_args)

        if operation == Operation.CREATE_EVENT.name:
            self.create_event(operation_args)

        if operation == Operation.CREATE_COMPLIANCE_POLICY.name:
            self.create_compliance_policy(operation_args)

        if operation == Operation.CHECK_COMPLIANCE.name:
            self.check_compliance_policy(operation_args)

        if operation == Operation.DELETE_COMPLIANCE.name:
            self.delete_compliance_policy("policy 1")

        # new line at the end of every operation
        print("")

    def create_asset(self, *args):
        """
        create_asset creates an asset given its behaviours and attributes and adds it to the
                     asset list.
        :asset_id: is a unique identity python can use to identify the asset (IT IS NOT Archivist related)
        :param attributes: the attributes in key value form.
        :type dictionary:
        """

        # parse the expected arguments
        arg = args[0]
        asset_id = parse_arg(arg, "asset_id")
        attributes = parse_arg(arg, "attributes")
        behaviours = parse_arg(arg, "behaviours", default=[])

        asset = self.client.assets.create(behaviours, attrs=attributes, confirm=True)
        print("Asset Created!")
        self.assets[asset_id] = asset

    def create_event(self, *args):
        """
        create_event creates an event for the given asset, based on its id.

        :param asset_id: a unique identity python can use to identify the asset (IT IS NOT Archivist related)
        """

        # parse the args
        arg = args[0]
        asset_id = parse_arg(arg, "asset_id")
        properties = parse_arg(arg, "properties", default={})
        attributes = parse_arg(arg, "attributes", default={})
        asset_attributes = parse_arg(arg, "asset_attributes", default={})

        # find the asset identity
        asset_identity = self.assets[asset_id]["identity"]

        # create the event
        event = self.client.events.create(asset_identity, props=properties, attrs=attributes, asset_attrs=asset_attributes, confirm=True)
        print("Event created!")

        self.events.append(event)

    def create_compliance_policy(self, *args):
        """
        create_compliance_policy creates a compliance policy
        :param policy_id: a unique identity python can use to identify the policy (IT IS NOT Archivist related)
        """

        # parse arguments
        arg = args[0]
        policy_id = parse_arg(arg, "policy_id")
        description = parse_arg(arg, "description")
        display_name = parse_arg(arg, "display_name")
        asset_filter = parse_arg(arg, "asset_filter")
        policy_type = parse_arg(arg, "policy_type")

        # richness args
        richness_assertions = parse_arg(arg, "richness_assertions", default=[])

        # dynamic tolerance args
        event_display_type = parse_arg(arg, "event_display_type", default="")
        closing_event_display_type = parse_arg(arg, "closing_event_display_type", default="")
        dynamic_window = parse_arg(arg, "dynamic_window", 0)
        dynamic_variability = parse_arg(arg, "dynamic_variability", 0.0)

        policy = self.client.compliance_policies.create(
            description,
            display_name,
            asset_filter,
            compliance_type=PolicyType[policy_type],
            richness_assertions=richness_assertions,
            event_display_type=event_display_type,
            closing_event_display_type=closing_event_display_type,
            dynamic_window=dynamic_window,
            dynamic_variability=dynamic_variability,
        )
        print("Policy Created!")

        self.policies[policy_id] = policy

    def check_compliance_policy(self, *args):
        """
        check_compliance_policy checks if the asset is compliant
        """

        # parse args
        arg = args[0]
        asset_id = parse_arg(arg, "asset_id")
        seconds_ago = parse_arg(arg, "seconds_ago", default=0)

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
            policy = self.client.compliance_policies.read(policy_outcome["compliance_policy_identity"])

            # print the policy name and the reason
            print("\tPolicy: {}. Reason: {}".format(policy["display_name"], policy_outcome["reason"]))

    def delete_compliance_policy(self, policy_id):
        """
        delete_compliance_policy deletes a given policy
        :param policy_id: a unique identity python can use to identify the policy (IT IS NOT Archivist related)
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

        for policy_id in self.policies.keys():
            self.delete_compliance_policy(policy_id)


def main():

    # create the argparser
    parser = argparse.ArgumentParser()

    parser.add_argument("url", help="the archivist url.")
    parser.add_argument("tokenfile", help="the auth token file location.")
    parser.add_argument("yamlfile", help="the yaml file describing the operations to conduct")

    args = parser.parse_args()

    manager = ArchivistStoryRunner(args.url, args.tokenfile, args.yamlfile)
    manager.run()

if __name__ == "__main__":
    main()
