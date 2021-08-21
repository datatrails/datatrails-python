"""Subjects interface

   Access to the subjects endpoint.

   The user is not expected to use this class directly. It is an attribute of the
   :class:`Archivist` class.

   For example instantiate an Archivist instance and execute the methods of the class:

   .. code-block:: python

      with open(".auth_token", mode="r") as tokenfile:
          authtoken = tokenfile.read().strip()

      # Initialize connection to Archivist
      arch = Archivist(
          "https://app.rkvst.io",
          auth=authtoken,
      )
      subject = arch.subjects.create(...)

"""

import logging
from typing import Dict, List, Optional

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from archivist import archivist as type_helper

from .constants import (
    SUBJECTS_SUBPATH,
    SUBJECTS_LABEL,
)
from .dictmerge import _deepmerge

#: Default page size - number of entities fetched in one REST GET in the
#: :func:`~_SubjectsClient.list` method. This can be overridden but should rarely
#: be changed.
DEFAULT_PAGE_SIZE = 500

FIXTURE_LABEL = "subjects"


LOGGER = logging.getLogger(__name__)


class Subject(dict):
    """Subject object"""


class _SubjectsClient:
    """SubjectsClient

    Access to subjects entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

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
            self.__query(
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
        return Subject(
            **self._archivist.post(
                f"{SUBJECTS_SUBPATH}/{SUBJECTS_LABEL}",
                data,
            )
        )

    def read(self, identity: str) -> Subject:
        """Read Subject

        Reads subject.

        Args:
            identity (str): subjects identity e.g. subjects/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Subject` instance

        """
        return Subject(
            **self._archivist.get(
                SUBJECTS_SUBPATH,
                identity,
            )
        )

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
                SUBJECTS_SUBPATH,
                identity,
                self.__query(
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
        return self._archivist.delete(SUBJECTS_SUBPATH, identity)

    def __query(
        self,
        *,
        display_name: Optional[str] = None,
        wallet_pub_keys: Optional[List[str]] = None,
        tessera_pub_keys: Optional[List[str]] = None,
    ) -> Dict:

        query = {}

        if display_name is not None:
            query["display_name"] = display_name

        if wallet_pub_keys is not None:
            query["wallet_pub_key"] = wallet_pub_keys

        if tessera_pub_keys is not None:
            query["tessera_pub_key"] = tessera_pub_keys

        return _deepmerge(self._archivist.fixtures.get(FIXTURE_LABEL), query)

    def count(self, *, display_name: Optional[str] = None) -> int:
        """Count subjects.

        Counts number of subjects that match criteria.

        Args:
            display_name (str): display name (optional)

        Returns:
            integer count of subjects.

        """
        return self._archivist.count(
            f"{SUBJECTS_SUBPATH}/{SUBJECTS_LABEL}",
            query=self.__query(display_name=display_name),
        )

    def list(
        self,
        *,
        page_size: int = DEFAULT_PAGE_SIZE,
        display_name: Optional[str] = None,
    ):
        """List subjects.

        List subjects that match criteria.
        TODO: filtering on display_name does not currently work

        Args:
            display_name (str): display name (optional)
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`Subject` instances

        """
        return (
            Subject(**a)
            for a in self._archivist.list(
                f"{SUBJECTS_SUBPATH}/{SUBJECTS_LABEL}",
                SUBJECTS_LABEL,
                page_size=page_size,
                query=self.__query(display_name=display_name),
            )
        )
