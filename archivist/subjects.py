"""Subjects interface

   Access to the subjects endpoint.

   The user is not expected to use this class directly. It is an attribute of the
   :class:`Archivist` class.

   For example instantiate an Archivist instance and execute the methods of the class:

   .. code-block:: python

      with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
          authtoken = tokenfile.read().strip()

      # Initialize connection to Archivist
      arch = Archivist(
          "https://app.datatrails.ai",
          authtoken,
      )
      subject = arch.subjects.create(...)

"""


from base64 import b64decode
from json import loads as json_loads
from logging import getLogger
from typing import TYPE_CHECKING, Any

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import subjects_confirmer
from .constants import (
    SUBJECTS_LABEL,
    SUBJECTS_SELF_ID,
    SUBJECTS_SUBPATH,
)
from .dictmerge import _deepmerge

if TYPE_CHECKING:
    from .archivist import Archivist

LOGGER = getLogger(__name__)


class Subject(dict):
    """Subject object"""


class _SubjectsClient:
    """SubjectsClient

    Access to subjects entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    maxDiff = None

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance
        self._subpath = f"{archivist_instance.root}/{SUBJECTS_SUBPATH}"
        self._label = f"{self._subpath}/{SUBJECTS_LABEL}"

    def __str__(self) -> str:
        return f"SubjectsClient({self._archivist.url})"

    def create(
        self,
        display_name: str,
        wallet_pub_key: "list[str]",
        tessera_pub_key: "list[str]",
    ) -> Subject:
        """Create subject

        Creates subject with defined attributes.

        Args:
            display_name (str): display name of subject.
            wallet_pub_key (list): wallet public keys
            tessera_pub_key (list): tessera public keys

        Returns:
            :class:`Subject` instance

        """
        LOGGER.debug("Create Subject %s", display_name)
        return self.create_from_data(
            self.__params(
                display_name=display_name,
                wallet_pub_key=wallet_pub_key,
                tessera_pub_key=tessera_pub_key,
            ),
        )

    def share(
        self, name: str, other_name: str, other_archivist: "Archivist"
    ) -> "tuple[Subject, Subject]":
        """Import the self subjects from the foreign archivist connection
           from another organization - mutually share.

        Args:
            name (str): display_name of the foreign self subject in this archivist
            other_name (str): display_name of the self subject in other archivist
            other_archivist (Archivist): Archivist object

        Returns:
            2-tuple of :class:`Subject` instance

        """
        subject1 = self.import_subject(
            name, other_archivist.subjects.read(SUBJECTS_SELF_ID)
        )
        subject2 = other_archivist.subjects.import_subject(
            other_name, self.read(SUBJECTS_SELF_ID)
        )
        subject1 = self.wait_for_confirmation(subject1["identity"])
        subject2 = other_archivist.subjects.wait_for_confirmation(subject2["identity"])

        return subject1, subject2

    def import_subject(self, display_name: str, subject: Subject) -> Subject:
        """Create subject from another subject usually
           from another organization.

        Args:
            display_name (str): display_name of the subject
            subject (Subject): Subject object

        Returns:
            :class:`Subject` instance

        """
        return self.create(
            display_name,
            subject["wallet_pub_key"],
            subject["tessera_pub_key"],
        )

    def create_from_data(self, data: "dict[str, Any]") -> Subject:
        """Create subject

        Creates subject with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of subject.

        Returns:
            :class:`Subject` instance

        """
        LOGGER.debug("Create Subject from data %s", data)
        return Subject(**self._archivist.post(self._label, data))

    def create_from_b64(self, data: "dict[str, Any]") -> Subject:
        """Create subject

        Creates subject with request body from b64 encoded string

        Args:
            data (dict): Dictionary with 2 fields:

        A YAML representation of the data argument would be:

            .. code-block:: yaml

                display_name: An imported subject
                subject_string: ey66...

        Returns:
            :class:`Subject` instance

        """
        decoded = b64decode(data["subject_string"])
        LOGGER.debug("decoded %s", decoded)
        outdata = {
            k: v
            for k, v in json_loads(decoded).items()
            if k in ("wallet_pub_key", "tessera_pub_key")
        }
        outdata["display_name"] = data["display_name"]
        LOGGER.debug("data %s", outdata)

        return Subject(**self._archivist.post(self._label, outdata))

    def wait_for_confirmation(self, identity: str) -> Subject:
        """Wait for subject to be confirmed.

        Waits for subject to be confirmed.

        Args:
            identity (str): identity of asset

        Returns:
            True if subject is confirmed.

        """
        subjects_confirmer.MAX_TIME = self._archivist.max_time
        # pylint: disable=protected-access
        return subjects_confirmer._wait_for_confirmation(self, identity)

    def read(self, identity: str) -> Subject:
        """Read Subject

        Reads subject.

        Args:
            identity (str): subjects identity e.g. subjects/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Subject` instance

        """
        return Subject(**self._archivist.get(f"{self._subpath}/{identity}"))

    def update(
        self,
        identity: str,
        *,
        display_name: "str|None" = None,
        wallet_pub_key: "list[str]|None" = None,
        tessera_pub_key: "list[str]|None" = None,
    ) -> Subject:
        """Update Subject

        Update subject.

        Args:
            identity (str): subjects identity e.g. subjects/xxxxxxxxxxxxxxxxxxxxxxx
            display_name (str): display name of subject.
            wallet_pub_key (list): wallet public keys
            tessera_pub_key (list): tessera public keys

        Returns:
            :class:`Subject` instance

        """
        return Subject(
            **self._archivist.patch(
                f"{self._subpath}/{identity}",
                self.__params(
                    display_name=display_name,
                    wallet_pub_key=wallet_pub_key,
                    tessera_pub_key=tessera_pub_key,
                ),
            )
        )

    def delete(self, identity: str) -> "dict[str, Any]":
        """Delete Subject

        Deletes subject.

        Args:
            identity (str): subjects identity e.g. subjects/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Subject` instance - empty?

        """
        return self._archivist.delete(f"{self._subpath}/{identity}")

    def __params(
        self,
        *,
        display_name: "str|None" = None,
        wallet_pub_key: "list[str]|None" = None,
        tessera_pub_key: "list[str]|None" = None,
    ) -> "dict[str, Any]":
        params = {}

        if display_name is not None:
            params["display_name"] = display_name

        if wallet_pub_key is not None:
            params["wallet_pub_key"] = wallet_pub_key

        if tessera_pub_key is not None:
            params["tessera_pub_key"] = tessera_pub_key

        return _deepmerge(self._archivist.fixtures.get(SUBJECTS_LABEL), params)

    def count(self, *, display_name: "str|None" = None) -> int:
        """Count subjects.

        Counts number of subjects that match criteria.

        Args:
            display_name (str): display name (optional)

        Returns:
            integer count of subjects.

        """
        return self._archivist.count(
            self._label,
            params=self.__params(display_name=display_name),
        )

    def list(
        self,
        *,
        page_size: "int|None" = None,
        display_name: "str|None" = None,
    ):
        """List subjects.

        List subjects that match criteria.

        Args:
            display_name (str): display name (optional)
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`Subject` instances

        """

        LOGGER.debug("List '%s'", display_name)
        return (
            Subject(**a)
            for a in self._archivist.list(
                self._label,
                SUBJECTS_LABEL,
                page_size=page_size,
                params=self.__params(display_name=display_name),
            )
        )
