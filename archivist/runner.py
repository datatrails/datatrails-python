"""
Base runner class for interpreting yaml story files.

"""

from __future__ import annotations
from collections import defaultdict
from functools import partialmethod
from json import dumps as json_dumps
from logging import getLogger
from operator import attrgetter
from time import sleep as time_sleep
from types import GeneratorType
from typing import Any, Callable, Optional, Tuple
from uuid import UUID

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
# pylint:disable=missing-function-docstring
# pylint:disable=protected-access
from .archivist import Archivist
from .confirmer import MAX_TIME
from .errors import ArchivistError, ArchivistInvalidOperationError
from .parser import get_auth

LOGGER = getLogger(__name__)


NOUNS = ("archivist", "access_policy", "asset", "location", "subject", "subject_import")


def tree():
    """Recursive dict of dicts"""
    return defaultdict(tree)


class _ActionMap(dict):
    """
    Map of actions and keywords for an action
    """

    # 'use_asset_label' gets the asset_idenity and can insert it in 3 places:
    #
    # 1. first positional argument
    # 2. keyword arguments with key
    # 3. keyword argument in first argument which is a dictionary.
    #
    #  use_asset_label = 1   = first positional argument
    #  use_asset_label = "asset_id"   = keyword argument
    #  use_asset_label = "-asset_id"   = keyword argument in first argumemt that is
    #                                    a dictionary
    # similarly for access_policy, location and subject labels
    #
    def __init__(self, archivist_instance: Optional[Archivist]):
        super().__init__()
        self.archivist = archivist_instance

        self["ARCHIVIST_CREATE"] = {
            "action": "archivist_create",
            "pos": ("url",),
            "keywords": (
                "auth_token",
                "client_id",
                "client_secret",
                "max_time",
                "verify",
            ),
            "set_archivist_label": True,
        }

        # please keep in alphabetical order
        self["ACCESS_POLICIES_COUNT"] = {
            "action": "archivist.access_policies.count",
            "keywords": ("display_name",),
            "use_archivist_label": "add_archivist",
        }
        self["ACCESS_POLICIES_CREATE"] = {
            "action": "archivist.access_policies.create_from_data",
            "delete": "archivist.access_policies.delete",
            "set_access_policy_label": True,
            "use_archivist_label": "add_archivist",
            "use_subject_import_label": "add_arg_identity",
        }
        self["ACCESS_POLICIES_LIST"] = {
            "action": "archivist.access_policies.list",
            "keywords": ("display_name",),
            "use_archivist_label": "add_archivist",
        }
        self["ACCESS_POLICIES_LIST_MATCHING_ASSETS"] = {
            "action": "archivist.access_policies.list_matching_assets",
            "use_archivist_label": "add_archivist",
        }
        self["ACCESS_POLICIES_LIST_MATCHING_ACCESS_POLICIES"] = {
            "action": "archivist.access_policies.list_matching_access_policies",
            "use_asset_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["ACCESS_POLICIES_READ"] = {
            "action": "archivist.access_policies.read",
            "use_access_policy_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["ACCESS_POLICIES_UPDATE"] = {
            "action": "archivist.access_policies.update",
            "keywords": (
                "display_name",
                "filters",
                "access_permissions",
            ),
            "use_access_policy_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["ASSETS_ATTACHMENT_INFO"] = {
            "action": "archivist.attachments.info",
            "use_asset_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["ASSETS_COUNT"] = {
            "action": "archivist.assets.count",
            "keywords": (
                "props",
                "attrs",
            ),
            "use_archivist_label": "add_archivist",
        }
        self["ASSETS_CREATE_IF_NOT_EXISTS"] = {
            "action": "archivist.assets.create_if_not_exists",
            "keywords": ("confirm",),
            "set_asset_label": True,
            "use_location_label": "add_data_location_identity",
            "use_archivist_label": "add_archivist",
        }
        self["ASSETS_CREATE"] = {
            "action": "archivist.assets.create_from_data",
            "keywords": ("confirm",),
            "set_asset_label": True,
            "use_archivist_label": "add_archivist",
        }
        self["ASSETS_LIST"] = {
            "action": "archivist.assets.list",
            "keywords": (
                "props",
                "attrs",
            ),
            "use_archivist_label": "add_archivist",
        }
        self["ASSETS_READ"] = {
            "action": "archivist.assets.read",
            "use_asset_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["ASSETS_WAIT_FOR_CONFIRMED"] = {
            "action": "archivist.assets.wait_for_confirmed",
            "keywords": (
                "props",
                "attrs",
            ),
            "use_archivist_label": "add_archivist",
        }
        self["COMPOSITE_ESTATE_INFO"] = {
            "action": "archivist.composite.estate_info",
            "use_archivist_label": "add_archivist",
        }
        self["COMPLIANCE_POLICIES_CREATE"] = {
            "action": "archivist.compliance_policies.create_from_data",
            "delete": "archivist.compliance_policies.delete",
            "use_archivist_label": "add_archivist",
        }
        self["COMPLIANCE_COMPLIANT_AT"] = {
            "action": "archivist.compliance.compliant_at",
            "keywords": ("report",),
            "use_asset_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["EVENTS_CREATE"] = {
            "action": "archivist.events.create_from_data",
            "keywords": ("confirm",),
            "use_asset_label": "add_arg_identity",
            "use_location_label": "add_data_location_identity",
            "use_archivist_label": "add_archivist",
        }
        self["EVENTS_COUNT"] = {
            "action": "archivist.events.count",
            "keywords": (
                "asset_id",
                "props",
                "attrs",
                "asset_attrs",
            ),
            "use_asset_label": "add_kwarg_asset_identity",
            "use_archivist_label": "add_archivist",
        }
        self["EVENTS_LIST"] = {
            "action": "archivist.events.list",
            "keywords": (
                "asset_id",
                "props",
                "attrs",
                "asset_attrs",
            ),
            "use_asset_label": "add_kwarg_asset_identity",
            "use_archivist_label": "add_archivist",
        }
        self["LOCATIONS_COUNT"] = {
            "action": "archivist.locations.count",
            "keywords": (
                "props",
                "attrs",
            ),
            "use_archivist_label": "add_archivist",
        }
        self["LOCATIONS_CREATE_IF_NOT_EXISTS"] = {
            "action": "archivist.locations.create_if_not_exists",
            "keywords": ("confirm",),
            "set_location_label": True,
            "use_archivist_label": "add_archivist",
        }
        self["LOCATIONS_LIST"] = {
            "action": "archivist.locations.list",
            "keywords": (
                "props",
                "attrs",
            ),
            "use_archivist_label": "add_archivist",
        }
        self["LOCATIONS_READ"] = {
            "action": "archivist.locations.read",
            "use_location_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["SUBJECTS_COUNT"] = {
            "action": "archivist.subjects.count",
            "keywords": ("display_name",),
            "use_archivist_label": "add_archivist",
        }
        self["SUBJECTS_CREATE"] = {
            "action": "archivist.subjects.create_from_data",
            "delete": "archivist.subjects.delete",
            "set_subject_label": True,
            "use_archivist_label": "add_archivist",
        }
        self["SUBJECTS_CREATE_FROM_B64"] = {
            "action": "archivist.subjects.create_from_b64",
            "delete": "archivist.subjects.delete",
            "set_subject_label": True,
            "use_archivist_label": "add_archivist",
        }
        self["SUBJECTS_DELETE"] = {
            "action": "archivist.subjects.delete",
            "use_subject_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["SUBJECTS_IMPORT"] = {
            "action": "archivist.subjects.import_subject",
            "pos": ("name",),
            "use_subject_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
            "set_subject_import_label": True,
        }
        self["SUBJECTS_LIST"] = {
            "action": "archivist.subjects.list",
            "keywords": ("display_name",),
            "use_archivist_label": "add_archivist",
        }
        self["SUBJECTS_READ"] = {
            "action": "archivist.subjects.read",
            "use_subject_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["SUBJECTS_SHARE"] = {
            "action": "archivist.subjects.share",
            "pos": ("name","other_name", "other_archivist",),
            "set_subjects_label": True,
            "use_archivist_label": "add_archivist",
        }
        self["SUBJECTS_UPDATE"] = {
            "action": "archivist.subjects.update",
            "keywords": (
                "display_name",
                "wallet_pub_key",
                "tessera_pub_key",
            ),
            "use_subject_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }
        self["SUBJECTS_WAIT_FOR_CONFIRMATION"] = {
            "action": "archivist.subjects.wait_for_confirmation",
            "use_subject_label": "add_arg_identity",
            "use_archivist_label": "add_archivist",
        }

    @staticmethod
    def archivist_create(
        url: str,
        *,
        auth_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        max_time: float = MAX_TIME,
        verify: bool = True,
    ) -> Archivist:
        auth = get_auth(
            auth_token=auth_token,
            client_id=client_id,
            client_secret=client_secret,
        )
        return Archivist(url, auth, max_time=max_time, verify=verify)

    def ops(self, action_name: str) -> dict[str, Any]:
        """
        Get valid entry in map
        """
        ops = self.get(action_name)
        if ops is None:
            raise ArchivistInvalidOperationError(f"Illegal Action '{action_name}'")
        return ops

    def action(self, action_name: str) -> Callable:
        """
        Get valid action in map
        """
        # if an exception occurs here then the dict initialised above is faulty.
        action = self.ops(action_name).get("action")
        return attrgetter(action)(self)  # type: ignore

    def keywords(self, action_name: str) -> Tuple | None:
        """
        Get keywords in map
        """
        return self.ops(action_name).get("keywords")

    def pos(self, action_name: str) -> Tuple | None:
        """
        Get positional args in map
        """
        return self.ops(action_name).get("pos")

    def delete(self, action_name: str) -> Optional[Callable]:
        """
        Get delete_method in map
        """
        delete = self.ops(action_name).get("delete")
        if delete is None:
            return None

        return attrgetter(delete)(self)  # type: ignore

    def label(self, noun: str, endpoint: str, action_name: str) -> bool:
        """
        Return whether this action uses or sets label
        """
        return self.ops(action_name).get(f"{noun}_{endpoint}_label", False)


class _Step(dict):  # pylint:disable=too-many-instance-attributes
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._archivist = None
        self._args: list[Any] = []
        self._kwargs: dict[str, Any] = {}
        self._actions = None
        self._action = None
        self._action_name = None
        self._data = {}
        self._keywords = None
        self._pos = None
        self._delete_method = None
        self._labels = {}
        self._labels["use"] = {}
        self._labels["set"] = {}

    def add_arg_identity(self, noun, entities):
        """Gets the identity of an entity previously created from its label
        and insert into the current positional argument
        (usually the first positional argument
        """
        identity = self.identity_from_label(noun, entities)
        self._args.append(identity)

    def add_archivist(self, noun, entities):
        """sets the current archivist object to one previously defined"""
        label = self.get(f"{noun}_label")
        self._archivist = entities[label]

    def add_kwarg_identity(self, key, noun, entities):
        """Gets the identity of an entity previously created from its label
        and insert into a keyword argument.

        This is used as a partial method for asset_id,location etc...
        """
        identity = self.identity_from_label(noun, entities)
        self._kwargs[key] = identity

    add_kwarg_asset_identity = partialmethod(add_kwarg_identity, "asset_id")

    def add_data_identity(self, key, noun, entities):
        """Gets the identity of an entity previously created from its label
        and insert into a data object.

        This is used as a partial method for location etc...
        """
        identity = self.identity_from_label(noun, entities)
        self._data[key] = {}
        self._data[key]["identity"] = identity

    add_data_location_identity = partialmethod(add_data_identity, "location")

    def args(self, entities, step):
        """
        Add args and kwargs to action.
        """
        self._args = []
        self._kwargs = {}

        for noun in NOUNS:
            label = self.get(f"{noun}_label")
            func = self.label("use", noun)
            if label is not None and func:
                getattr(self, func)(noun, entities)

        self.actions.archivist = (
            self._archivist
            if self.actions.archivist is None
            else self.actions.archivist
        )

        # keys are values that must be removed from the body of the request.
        # These are typically 'confirm' or 'report'. Some of the actions
        # have longer lists of keywords - these actions will be simplified
        # when dataclasses are introduced and this code will be much simpler.
        keys = []
        keywords = self.keywords
        if keywords is not None and len(keywords) > 0:
            keys.extend(keywords)
            for k in keywords:
                if k in step:
                    self._kwargs[k] = step[k]

        if self.pos:
            self._args = [step[pos] for pos in self.pos]
            keys.extend(self.pos)

        # add the request body to the positional arguments...
        self._data = {k: v for k, v in step.items() if k not in keys}

        if self._data:
            self._args.append(self._data)

        LOGGER.debug("pos args %s", self._args)

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

    def label(self, verb: str, noun: str):
        if self._labels[verb].get(noun) is None:
            self._labels[verb][noun] = self.actions.label(verb, noun, self.action_name)

        return self._labels[verb][noun]

    def identity_from_label(self, noun, entities):
        label = self.get(f"{noun}_label")

        # If it is a label, get the identity from previously created entity
        if not label.startswith(f"{noun}s/"):  # type: ignore
            identity = entities[label]["identity"]
            if isinstance(identity, str):
                return identity

            raise ArchivistInvalidOperationError(f"unknown {noun}")

        # else treat the value as an actual identity of the form {noun}s/{uuid}
        uid = label.split("/")[1]  # type: ignore
        try:
            _ = UUID(uid, version=4)
        except ValueError as exc:
            raise ArchivistInvalidOperationError(f"invalid {noun}s/{uid}") from exc

        return label

    def description(self):
        """emit description field if required"""
        description = self.get("description")
        if description is not None:
            LOGGER.info(description)

    @property
    def delete(self):
        """action might have a delete method"""
        return self.get("delete")

    def print_response(self, response):
        """print json response if required"""
        print_response = self.get("print_response")
        if print_response:
            # some responses are generators...
            if isinstance(response, GeneratorType):
                for e in response:
                    LOGGER.info("Response %s", json_dumps(e, indent=4))
            else:
                LOGGER.info("Response %s", json_dumps(response, indent=4))

    def wait_time(self):
        """wait if required"""
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
    def action(self) -> Callable:
        if self._action is None:
            self._action = self.actions.action(self.action_name)

        return self._action

    @property
    def delete_method(self) -> Optional[Callable]:
        if self._delete_method is None:
            self._delete_method = self.actions.delete(self.action_name)

        return self._delete_method

    @property
    def keywords(self):
        if self._keywords is None:
            self._keywords = self.actions.keywords(self.action_name)

        return self._keywords

    @property
    def pos(self):
        if self._pos is None:
            self._pos = self.actions.pos(self.action_name)

        return self._pos

    @property
    def action_name(self):
        if self._action_name is None:
            action_name = self.get("action")
            if action_name is None:
                raise ArchivistInvalidOperationError("Missing Action")

            self._action_name = action_name

        return self._action_name


class Runner:
    """
    ArchivistRunner takes a url, token_file.
    """

    def __init__(self):
        self.entities = tree()
        self.deletions = {}

    def __str__(self) -> str:
        return "Runner()"

    def __call__(self, config: dict[str, Any]):
        """
        The dict config contains a list of `steps` to be performed serially, e.g.

        ```
        "steps": [
            {
                "step": {
                    "action": "ASSETS_CREATE",
                    "description": "Create a Radiation bag number one",
                    "wait_time": 10,
                    "archivist_label": "ACME Corporation",
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

    def run_steps(self, config: dict[str, Any]):
        """Runs all defined steps in self.config."""
        for step in config["steps"]:
            self.run_step(step)

        self.delete()

    def run_step(self, step: dict[str, Any]):
        """Runs a step given parameters and the type of step.

        Args:
            step (dict): the steps map.
        """

        # get step settings
        s = _Step(**step.pop("step"))

        # output description
        s.description()
        s.args(self.entities, step)

        # wait for a number of seconds and then execute
        s.wait_time()
        response = s.execute()

        s.print_response(response)

        if s.delete:
            self.set_deletions(response, s.delete_method)

        for noun in NOUNS:
            label = s.get(f"{noun}_label")
            if s.label("set", noun) and label is not None:
                self.entities[label] = response

    def set_deletions(self, response: dict[str, Any], delete_method):
        """sets entry to be deleted"""

        if delete_method is not None:
            identity = response["identity"]
            self.deletions[identity] = delete_method

    def delete(self):
        """Deletes all entities"""
        for identity, delete_method in self.deletions.items():
            LOGGER.info("Delete %s", identity)
            delete_method(identity)
