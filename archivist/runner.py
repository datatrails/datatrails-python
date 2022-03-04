"""
Base runner class for interpreting yaml story files.

"""

from collections import defaultdict
from json import dumps as json_dumps
from logging import getLogger
from types import GeneratorType
from time import sleep as time_sleep
from typing import Dict, Optional, Tuple

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
# pylint:disable=missing-function-docstring
# pylint:disable=protected-access
from . import archivist as type_helper
from .errors import ArchivistError, ArchivistInvalidOperationError

LOGGER = getLogger(__name__)


def tree():
    """Recursive dict of dicts"""
    return defaultdict(tree)


class _ActionMap(dict):
    """
    Map of actions and keywords for an action
    """

    def __init__(self, archivist: "type_helper.Archivist"):
        super().__init__()
        self["ASSETS_ATTACHMENT_INFO"] = {
            "action": archivist.attachments.info,
            "keywords": ("asset_or_event_id",),
            "use_asset_id": True,
        }
        self["ASSETS_CREATE_IF_NOT_EXISTS"] = {
            "action": archivist.assets.create_if_not_exists,
            "keywords": ("confirm",),
            "set_asset_id": True,
        }
        self["ASSETS_CREATE"] = {
            "action": archivist.assets.create_from_data,
            "keywords": ("confirm",),
            "set_asset_id": True,
        }
        self["ASSETS_LIST"] = {
            "action": archivist.assets.list,
            "keywords": (
                "props",
                "attrs",
            ),
        }
        self["ASSETS_COUNT"] = {
            "action": archivist.assets.count,
            "keywords": (
                "props",
                "attrs",
            ),
        }
        self["COMPOSITE_ESTATE_INFO"] = {
            "action": archivist.composite.estate_info,
        }
        self["COMPLIANCE_POLICIES_CREATE"] = {
            "action": archivist.compliance_policies.create_from_data,
            "delete": archivist.compliance_policies.delete,
        }
        self["COMPLIANCE_COMPLIANT_AT"] = {
            "action": archivist.compliance.compliant_at,
            "keywords": ("report",),
        }
        self["EVENTS_CREATE"] = {
            "action": archivist.events.create_from_data,
            "keywords": ("confirm",),
            "use_asset_id": True,
        }
        self["EVENTS_COUNT"] = {
            "action": archivist.events.count,
            "keywords": (
                "asset_id",
                "props",
                "attrs",
                "asset_attrs",
            ),
            "use_asset_id": True,
        }
        self["EVENTS_LIST"] = {
            "action": archivist.events.list,
            "keywords": (
                "asset_id",
                "props",
                "attrs",
                "asset_attrs",
            ),
            "use_asset_id": True,
        }
        self["LOCATIONS_COUNT"] = {
            "action": archivist.locations.count,
            "keywords": (
                "props",
                "attrs",
            ),
        }

    def ops(self, action_name: str) -> Dict:
        """
        Get valid entry in map
        """
        ops = self.get(action_name)
        if ops is None:
            raise ArchivistInvalidOperationError(f"Illegal Action '{action_name}'")
        return ops

    def action(self, action_name: str) -> Dict:
        """
        Get valid action in map
        """
        # if an exception occurs here then the dict initialised above is faulty.
        return self.ops(action_name).get("action")

    def keywords(self, action_name: str) -> Tuple:
        """
        Get keywords in map
        """
        return self.ops(action_name).get("keywords")

    def delete(self, action_name: str):
        """
        Get delete_method in map
        """
        return self.ops(action_name).get("delete")

    def use_asset_id(self, action_name: str) -> bool:
        """
        Return whether this action uses asset_id
        """
        return self.ops(action_name).get("use_asset_id", False)

    def set_asset_id(self, action_name: str) -> bool:
        """
        Return whether this action sets asset_id
        """
        return self.ops(action_name).get("set_asset_id", False)


class _Step(dict):  # pylint:disable=too-many-instance-attributes
    def __init__(self, archivist: "type_helper.Archivist", **kwargs):
        super().__init__(**kwargs)
        self._archivist = archivist
        self._args = None
        self._kwargs = None
        self._actions = None
        self._action = None
        self._action_name = None
        self._keywords = None
        self._delete_method = None
        self._use_asset_id = None
        self._set_asset_id = None

    def args(self, asset_id_method):
        """
        Positional arguments to action.
        """
        if self._args is None:
            args = []

            # get asset identity and prepend to the list of positional
            # arguments.  This will be simplified when dataclasses are
            # introduced.
            LOGGER.debug("self.asset_label %s", self.asset_label)
            LOGGER.debug("self.use_asset_id %s", self.use_asset_id)
            if not self.set_asset_id and self.asset_label is not None:
                asset_id = asset_id_method(self.asset_label)
                if asset_id is None:
                    raise ArchivistInvalidOperationError(
                        f"Unknown Entity '{self.asset_label}'"
                    )

                # prepend if not specified in the keywords for the action.
                keywords = self.keywords
                if keywords is not None and "asset_id" not in keywords:
                    args.append(asset_id)

            self._args = args

        return self._args

    def kwargs(self, asset_id_method, step):
        if self._kwargs is None:
            kwargs = {}

            # keys are values that must be removed from the body of the request.
            # These are typically 'confirm' or 'report'. Some of the actions
            # have longer lists of keywords - these actions will be simplified
            # when dataclasses are introduced and this code will be much simpler.
            keys = []
            keywords = self.keywords
            if keywords is not None and len(keywords) > 0:
                keys.extend(keywords)
                if "asset_id" in keywords and self.asset_label is not None:
                    kwargs["asset_id"] = asset_id_method(self.asset_label)

                for k in keywords:
                    if k in step:
                        kwargs[k] = step[k]

            self._kwargs = kwargs
            LOGGER.debug("keys %s", keys)

            # add the request body to the positional arguments...
            data = {k: v for k, v in step.items() if k not in keys}
            if data:
                self._args.append(data)

        return self._kwargs

    def execute(self):
        action = self.action
        LOGGER.debug("action %s", action)
        LOGGER.debug("args %s", self._args)
        if len(self._kwargs) > 0:
            LOGGER.debug("kwargs %s", self._kwargs)
            response = action(*self._args, **self._kwargs)
        else:
            response = action(*self._args)

        # Some actions return a tuple
        if isinstance(response, tuple):
            response = response[0]

        return response

    @property
    def asset_label(self):
        return self.get("asset_label")

    def description(self):
        description = self.get("description")
        if description is not None:
            LOGGER.info(description)

    @property
    def delete(self):
        return self.get("delete")

    def print_response(self, response):
        print_response = self.get("print_response")
        if print_response:
            # some responses are generators...
            if isinstance(response, GeneratorType):
                for e in response:
                    LOGGER.info("Response %s", json_dumps(e, indent=4))
            else:
                LOGGER.info("Response %s", json_dumps(response, indent=4))

    def wait_time(self):
        wait_time = self.get("wait_time", 0)
        if wait_time > 0:
            LOGGER.info("Waiting for %d seconds", wait_time)
            time_sleep(wait_time)

    @property
    def actions(self):
        if self._actions is None:
            self._actions = _ActionMap(self._archivist)

        return self._actions

    @property
    def action(self):
        if self._action is None:
            self._action = self.actions.action(self.action_name)

        return self._action

    @property
    def delete_method(self):
        if self._delete_method is None:
            self._delete_method = self.actions.delete(self.action_name)

        return self._delete_method

    @property
    def use_asset_id(self):
        if self._use_asset_id is None:
            self._use_asset_id = self.actions.use_asset_id(self.action_name)

        return self._use_asset_id

    @property
    def set_asset_id(self):
        if self._set_asset_id is None:
            self._set_asset_id = self.actions.set_asset_id(self.action_name)

        return self._set_asset_id

    @property
    def keywords(self):
        if self._keywords is None:
            self._keywords = self.actions.keywords(self.action_name)

        return self._keywords

    @property
    def action_name(self):
        if self._action_name is None:
            action_name = self.get("action")
            if action_name is None:
                raise ArchivistInvalidOperationError("Missing Action")

            self._action_name = action_name

        return self._action_name


class _Runner:
    """
    ArchivistRunner takes a url, token_file.
    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist
        self.entities = None
        self.deletions = {}
        self._step = None

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

        # get step settings
        s = _Step(self._archivist, **step.pop("step"))

        # output description
        s.description()

        # this is a bit clunky...
        s.args(self.asset_id)
        s.kwargs(self.asset_id, step)

        # wait for a number of seconds and then execute
        s.wait_time()
        response = s.execute()

        s.print_response(response)

        if s.delete:
            self.set_deletions(response, s.delete_method)

        if s.set_asset_id:
            self.set_entities(s.asset_label, response)

    def set_entities(self, asset_label: str, response: Dict):
        """sets entties entry"""

        if asset_label:
            self.entities[asset_label] = response

    def set_deletions(self, response: Dict, delete_method):
        """sets entry to be deleted"""

        if delete_method is not None:
            identity = response["identity"]
            self.deletions[identity] = delete_method

    def delete(self):
        """Deletes all entities"""
        for identity, delete_method in self.deletions.items():
            LOGGER.info("Delete %s", identity)
            delete_method(identity)

    def asset_id(self, name: str) -> Optional[str]:
        """Gets entity id"""

        asset_id = self.entities[name]["identity"]
        if isinstance(asset_id, str):
            return asset_id

        return None
