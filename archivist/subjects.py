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
          "https://app.rkvst.io",
          authtoken,
      )
      subject = arch.subjects.create(...)

"""

from base64 import b64decode
from json import loads as json_loads
from logging import getLogger
from typing import Dict, List, Optional

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper  # pylint:disable=unused-import

from .constants import (
    SUBJECTS_SUBPATH,
    SUBJECTS_LABEL,
)
from . import subjects_confirmer
from .dictmerge import _deepmerge


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

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist
        self._subpath = f"{archivist.root}/{SUBJECTS_SUBPATH}"
        self._label = f"{self._subpath}/{SUBJECTS_LABEL}"

    def __str__(self) -> str:
        return f"SubjectsClient({self._archivist.url})"

    def create(
        self, display_name: str, wallet_pub_keys: List, tessera_pub_keys: List
    ) -> Subject:
        """Create subject

        Creates subject with defined attributes.

        Args:
            display_name (str): display name of subject.
            wallet_pub_keys (list): wallet public keys
            tessera_pub_keys (list): tessera public keys

        Returns:
            :class:`Subject` instance

        """
        LOGGER.debug("Create Subject %s", display_name)
        return self.create_from_data(
            self.__params(
                display_name=display_name,
                wallet_pub_keys=wallet_pub_keys,
                tessera_pub_keys=tessera_pub_keys,
            ),
        )

    def create_from_data(self, data: Dict) -> Subject:
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

    def create_from_b64(self, data: Dict) -> Subject:
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
        display_name: str = None,
        wallet_pub_keys: Optional[List[str]] = None,
        tessera_pub_keys: Optional[List[str]] = None,
    ) -> Subject:
        """Update Subject

        Update subject.

        Args:
            identity (str): subjects identity e.g. subjects/xxxxxxxxxxxxxxxxxxxxxxx
            display_name (str): display name of subject.
            wallet_pub_keys (list): wallet public keys
            tessera_pub_keys (list): tessera public keys

        Returns:
            :class:`Subject` instance

        """
        return Subject(
            **self._archivist.patch(
                f"{self._subpath}/{identity}",
                self.__params(
                    display_name=display_name,
                    wallet_pub_keys=wallet_pub_keys,
                    tessera_pub_keys=tessera_pub_keys,
                ),
            )
        )

    def delete(self, identity: str) -> Dict:
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
        display_name: Optional[str] = None,
        wallet_pub_keys: Optional[List[str]] = None,
        tessera_pub_keys: Optional[List[str]] = None,
    ) -> Dict:

        params = {}

        if display_name is not None:
            params["display_name"] = display_name

        if wallet_pub_keys is not None:
            params["wallet_pub_key"] = wallet_pub_keys

        if tessera_pub_keys is not None:
            params["tessera_pub_key"] = tessera_pub_keys

        return _deepmerge(self._archivist.fixtures.get(SUBJECTS_LABEL), params)

    def count(self, *, display_name: Optional[str] = None) -> int:
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
        page_size: Optional[int] = None,
        display_name: Optional[str] = None,
    ):
        """List subjects.

        List subjects that match criteria.

        Args:
            display_name (str): display name (optional)
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`Subject` instances

        """
        return (
            Subject(**a)
            for a in self._archivist.list(
                self._label,
                SUBJECTS_LABEL,
                page_size=page_size,
                params=self.__params(display_name=display_name),
            )
        )
