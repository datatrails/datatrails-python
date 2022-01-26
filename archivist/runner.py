"""
Base runner class for interpreting yaml story files.

"""

from collections import defaultdict
from json import dumps as json_dumps
from logging import getLogger
from time import sleep as time_sleep
from typing import Dict, Optional

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper
from .errors import ArchivistError, ArchivistInvalidOperationError

LOGGER = getLogger(__name__)


def tree():
    """Recursive dicts of dicts"""
    return defaultdict(tree)


class _Runner:
    """
    ArchivistRunner takes a url, token_file.
    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist
        self.entities = None
        self._actions = {
            "ASSETS_CREATE": archivist.assets.create_from_data,
            "EVENTS_CREATE": archivist.events.create_from_data,
            "COMPLIANCE_POLICIES_CREATE": archivist.compliance_policies.create_from_data,
            "COMPLIANCE_COMPLIANT_AT": archivist.compliance.compliant_at,
        }

    def __str__(self) -> str:
        return f"Runner({self._archivist.url})"

    def __call__(self, config: Dict):
        """
        The dict config contains a list of `steps` to be performed serially, e.g.

        ```
        "steps": [
            {
                "step": {
                    "action": "ASSETS_CREATE",
                    "description": "Create a Radiation bag number one",
                    "wait_time": 10,
                },
                "attributes": {
                    "arc_display_name": "radiation bag 1",
                    "radioactive": True,
                    "radiation_level": 0,
                    "weight": 0,
                },
                "confirm": True,
            }
        ]
        ```

        where:
         - `action` is the operation to perform.
         - `description` is what to print to the console.
         - `wait_time` is time to wait before running the operation.
         - `attributes` are the asset's attributes

        To perform all the steps call the class instance.
        """
        try:
            self.run_steps(config)
        except (ArchivistError, KeyError) as ex:
            LOGGER.info("Runner exception %s", ex)

    def run_steps(self, config: Dict):
        """Runs all defined steps in self.config."""
        self.entities = tree()
        for step in config["steps"]:
            self.run_step(step)

        self.delete()

    def run_step(self, step: Dict):
        """Runs a step given parameters and the type of step.

        Args:
            step (dict): the steps map.
        """

        s = step["step"]
        action_name = s.get("action")
        if action_name is None:
            raise ArchivistInvalidOperationError("Missing Action")

        action = self._actions.get(action_name)
        if action is None:
            raise ArchivistInvalidOperationError(f"Illegal Action {action_name}")

        description = s.get("description")
        if description is not None:
            LOGGER.info(description)

        # wait for a number of seconds
        wait_time = s.get("wait_time", 0)
        if wait_time > 0:
            LOGGER.info("Waiting for %d seconds", wait_time)
            time_sleep(wait_time)

        # sort out argumenst to action method.
        # XXXX: add inspect.signature calls to validate ...
        # (at the moment we will get an upstream error if the step is incorrect)
        args = []
        asset_name = s.get("asset_name")

        asset_id = self.asset_id(asset_name)
        if asset_id is not None:
            args.append(asset_id)

        kwargs = {}
        data = {k: v for k, v in step.items() if k not in ("step", "confirm")}
        if data:
            args.append(data)
        LOGGER.debug("args %s", args)

        if "confirm" in step:
            kwargs["confirm"] = step["confirm"]
            LOGGER.debug("kwargs %s", kwargs)
            response = action(*args, **kwargs)
        else:
            response = action(*args)

        print_response = s.get("print_response")
        if print_response:
            LOGGER.info("Response %s", json_dumps(response, indent=4))

        self.set_entities(action_name, response)

        if action_name == "COMPLIANCE_COMPLIANT_AT" and not response["compliant"]:
            self.process_compliant_at(response)

    def set_entities(self, action_name: str, response: Dict):
        """sets entties entry"""

        try:
            name = response.name
        except AttributeError:
            pass
        else:
            if name is not None:
                self.entities[action_name][name] = response

    def process_compliant_at(self, response: Dict):
        """Evaluates Gets asset id"""

        # if there is a reason print it
        for outcome in response["compliance"]:

            if outcome["compliant"]:
                continue

            # get the compliance policy
            policy = self._archivist.compliance_policies.read(
                outcome["compliance_policy_identity"]
            )

            # print the policy name and the reason
            LOGGER.info(
                "NON-COMPLIANCE -> Policy: %s: Reason %s",
                policy["display_name"],
                outcome["reason"],
            )

    def asset_id(self, asset_name: str) -> Optional[str]:
        """Gets asset id"""

        if asset_name is not None:
            asset_id = self.entities["ASSETS_CREATE"][asset_name]["identity"]
            if isinstance(asset_id, str):
                return asset_id

        return None

    def delete(self):
        """Deletes all policies

        Just compliance policies for now
        """
        for k, v in self.entities["COMPLIANCE_POLICIES_CREATE"].items():
            LOGGER.info("Delete %s -> %s", k, v["identity"])
            self._archivist.compliance_policies.delete(v["identity"])
