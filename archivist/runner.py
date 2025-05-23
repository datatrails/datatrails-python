"""
Base runner class for interpreting yaml story files.

"""

from collections import defaultdict
from functools import partialmethod
from json import dumps as json_dumps
from logging import getLogger
from time import sleep as time_sleep
from types import GeneratorType
from typing import TYPE_CHECKING, Any

from .errors import ArchivistError, ArchivistInvalidOperationError

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
# pylint:disable=missing-function-docstring
# pylint:disable=protected-access
if TYPE_CHECKING:
    from .archivist import Archivist

LOGGER = getLogger(__name__)


NOUNS = ("asset", "subject")


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
    # similarly for subjects labels
    #
    def __init__(self, archivist_instance: "Archivist"):
        super().__init__()
        self._archivist = archivist_instance

        # please keep in alphabetical order
        self["ASSETS_ATTACHMENT_INFO"] = {
            "action": self._archivist.attachments.info,
            "use_asset_label": "add_arg_identity",
        }
        self["ASSETS_COUNT"] = {
            "action": self._archivist.assets.count,
            "keywords": (
                "props",
                "attrs",
            ),
        }
        self["ASSETS_CREATE_IF_NOT_EXISTS"] = {
            "action": self._archivist.assets.create_if_not_exists,
            "keywords": ("confirm",),
            "set_asset_label": True,
        }
        self["ASSETS_CREATE"] = {
            "action": self._archivist.assets.create_from_data,
            "keywords": ("confirm",),
            "set_asset_label": True,
        }
        self["ASSETS_LIST"] = {
            "action": self._archivist.assets.list,
            "keywords": (
                "props",
                "attrs",
            ),
        }
        self["ASSETS_WAIT_FOR_CONFIRMED"] = {
            "action": self._archivist.assets.wait_for_confirmed,
            "keywords": (
                "props",
                "attrs",
            ),
        }
        self["COMPOSITE_ESTATE_INFO"] = {
            "action": self._archivist.composite.estate_info,
        }
        self["EVENTS_CREATE"] = {
            "action": self._archivist.events.create_from_data,
            "keywords": ("confirm",),
            "use_asset_label": "add_arg_identity",
        }
        self["EVENTS_COUNT"] = {
            "action": self._archivist.events.count,
            "keywords": (
                "asset_id",
                "props",
                "attrs",
                "asset_attrs",
            ),
            "use_asset_label": "add_kwarg_asset_identity",
        }
        self["EVENTS_LIST"] = {
            "action": self._archivist.events.list,
            "keywords": (
                "asset_id",
                "props",
                "attrs",
                "asset_attrs",
            ),
            "use_asset_label": "add_kwarg_asset_identity",
        }
        self["SUBJECTS_COUNT"] = {
            "action": self._archivist.subjects.count,
            "keywords": ("display_name",),
        }
        self["SUBJECTS_CREATE"] = {
            "action": self._archivist.subjects.create_from_data,
            "delete": self._archivist.subjects.delete,
            "set_subject_label": True,
        }
        self["SUBJECTS_CREATE_FROM_B64"] = {
            "action": self._archivist.subjects.create_from_b64,
            "delete": self._archivist.subjects.delete,
            "set_subject_label": True,
        }
        self["SUBJECTS_DELETE"] = {
            "action": self._archivist.subjects.delete,
            "use_subject_label": "add_arg_identity",
        }
        self["SUBJECTS_LIST"] = {
            "action": self._archivist.subjects.list,
            "keywords": ("display_name",),
        }
        self["SUBJECTS_READ"] = {
            "action": self._archivist.subjects.read,
            "use_subject_label": "add_arg_identity",
        }
        self["SUBJECTS_UPDATE"] = {
            "action": self._archivist.subjects.update,
            "keywords": (
                "display_name",
                "wallet_pub_key",
                "tessera_pub_key",
            ),
            "use_subject_label": "add_arg_identity",
        }
        self["SUBJECTS_WAIT_FOR_CONFIRMATION"] = {
            "action": self._archivist.subjects.wait_for_confirmation,
            "use_subject_label": "add_arg_identity",
        }

    def ops(self, action_name: str):
        """
        Get valid entry in map
        """
        ops = self.get(action_name)
        if ops is None:
            raise ArchivistInvalidOperationError(f"Illegal Action '{action_name}'")
        return ops

    def action(self, action_name: str):
        """
        Get valid action in map
        """
        # if an exception occurs here then the dict initialized above is faulty.
        return self.ops(action_name).get("action")  # pyright: ignore

    def keywords(self, action_name: str):
        """
        Get keywords in map
        """
        return self.ops(action_name).get("keywords")

    def delete(self, action_name: str):
        """
        Get delete_method in map
        """
        return self.ops(action_name).get("delete")

    def label(self, noun: str, endpoint: str, action_name: str):
        """
        Return whether this action uses or sets label
        """
        return self.ops(action_name).get(f"{noun}_{endpoint}_label", False)


class _Step(dict):  # pylint:disable=too-many-instance-attributes
    def __init__(self, archivist_instance: "Archivist", **kwargs):
        super().__init__(**kwargs)
        self._archivist = archivist_instance
        self._args: "list[Any]" = []
        self._kwargs = {}
        self._actions = None
        self._action = None
        self._action_name = None
        self._data = {}
        self._keywords = None
        self._delete_method = None
        self._labels = {}
        self._labels["use"] = {}
        self._labels["set"] = {}

    def add_arg_identity(self, identity):
        self._args.append(identity)

    def add_kwarg_identity(self, key, identity):
        self._kwargs[key] = identity

    add_kwarg_asset_identity = partialmethod(add_kwarg_identity, "asset_id")

    def init_args(self, identity_method, step):
        """
        Add args and kwargs to action.
        """
        self._args = []
        self._kwargs = {}

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

        # add the request body to the positional arguments...
        self._data = {k: v for k, v in step.items() if k not in keys}

        for noun in NOUNS:
            label = self.get(f"{noun}_label")
            func = self.label("use", noun)
            if label is not None and func:
                identity = self.identity_from_label(noun, identity_method)
                if identity is None:
                    raise ArchivistInvalidOperationError(f"unknown {noun} '{label}'")

                getattr(self, func)(identity)

        if self._data:
            self._args.append(self._data)

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

    def identity_from_label(self, noun, identity_method):
        label = self.get(f"{noun}_label")
        return identity_method(label)

    def description(self):
        description = self.get("description")
        if description is not None:
            LOGGER.info(description)

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
    def args(self):
        return self._args

    @property
    def action(self):
        if self._action is None:
            self._action = self.actions.action(self.action_name)

        return self._action

    @property
    def delete_method(self):
        self._delete_method = self.actions.delete(self.action_name)

        return self._delete_method

    @property
    def keywords(self):
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

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance
        self.entities: defaultdict
        self.deletions = {}

    def __str__(self) -> str:
        return f"Runner({self._archivist.url})"

    def __call__(self, config: "dict[str, Any]"):
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

    def run_steps(self, config: "dict[str, Any]"):
        """Runs all defined steps in self.config."""
        self.entities = tree()
        for step in config["steps"]:
            self.run_step(step)

        self._archivist.close()

    def run_step(self, step: "dict[str, Any]"):
        """Runs a step given parameters and the type of step.

        Args:
            step (dict): the steps map.
        """

        # get step settings
        s = _Step(self._archivist, **step.pop("step"))

        # output description
        s.description()

        # this is a bit clunky...
        s.init_args(self.identity, step)

        # wait for a number of seconds and then execute
        s.wait_time()
        response = s.execute()

        s.print_response(response)

        for noun in NOUNS:
            label = s.get(f"{noun}_label")
            if s.label("set", noun) and label is not None:
                self.entities[label] = response

    def identity(self, name: str) -> "str|None":
        """Gets entity id"""

        identity = self.entities[name]["identity"]
        if isinstance(identity, str):
            return identity

        return None
