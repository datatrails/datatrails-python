"""Applications interface

   Access to the applications endpoint.

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
      application = arch.applications.create(...)

"""

from __future__ import annotations
from logging import getLogger
from typing import Any, Optional

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist

from .constants import (
    APPLICATIONS_SUBPATH,
    APPLICATIONS_LABEL,
    APPLICATIONS_REGENERATE,
)
from .dictmerge import _deepmerge


LOGGER = getLogger(__name__)


class Application(dict):
    """Application object"""


class _ApplicationsClient:
    """ApplicationsClient

    Access to applications entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: archivist.Archivist):
        self._archivist = archivist_instance
        self._subpath = f"{archivist_instance.root}/{APPLICATIONS_SUBPATH}"
        self._label = f"{self._subpath}/{APPLICATIONS_LABEL}"

    def __str__(self) -> str:
        return f"ApplicationsClient({self._archivist.url})"

    def create(self, display_name: str, custom_claims: dict[str, str]) -> Application:
        """Create application

        Creates application with defined attributes.

        Args:
            display_name (str): display name of application.
            custom_claims (dict): custom claims

        Returns:
            :class:`Application` instance

        """
        LOGGER.debug("Create Application %s", display_name)
        return self.create_from_data(
            self.__params(
                display_name=display_name,
                custom_claims=custom_claims,
            ),
        )

    def create_from_data(self, data: dict[str, Any]) -> Application:
        """Create application

        Creates application with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of application.

        Returns:
            :class:`Application` instance

        """
        return Application(**self._archivist.post(self._label, data))

    def read(self, identity: str) -> Application:
        """Read Application

        Reads application.

        Args:
            identity (str): applications identity e.g. applications/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Application` instance

        """
        return Application(**self._archivist.get(f"{self._subpath}/{identity}"))

    def update(
        self,
        identity: str,
        *,
        display_name: Optional[str] = None,
        custom_claims: Optional[dict[str, str]] = None,
    ) -> Application:
        """Update Application

        Update application.

        Args:
            identity (str): applications identity e.g. applications/xxxxxxxxxxxxxxxxxxxxxxx
            display_name (str): display name of application.
            custom_claims (dict): custom claims

        Returns:
            :class:`Application` instance

        """
        return Application(
            **self._archivist.patch(
                f"{self._subpath}/{identity}",
                self.__params(
                    display_name=display_name,
                    custom_claims=custom_claims,
                ),
            )
        )

    def delete(self, identity: str) -> dict[str, Any]:
        """Delete Application

        Deletes application.

        Args:
            identity (str): applications identity e.g. applications/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Application` instance - empty?

        """
        return self._archivist.delete(f"{self._subpath}/{identity}")

    def __params(
        self,
        *,
        display_name: Optional[str] = None,
        custom_claims: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:

        params = {}

        if display_name is not None:
            params["display_name"] = display_name

        if custom_claims is not None:
            params["custom_claims"] = custom_claims

        return _deepmerge(self._archivist.fixtures.get(APPLICATIONS_LABEL), params)

    def list(
        self,
        *,
        page_size: Optional[int] = None,
        display_name: Optional[str] = None,
    ):
        """List applications.

        List applications that match criteria.

        Args:
            display_name (str): display name (optional)
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`Application` instances

        """
        return (
            Application(**a)
            for a in self._archivist.list(
                self._label,
                APPLICATIONS_LABEL,
                page_size=page_size,
                params=self.__params(display_name=display_name),
            )
        )

    def regenerate(self, identity: str) -> Application:
        """Regenerate secret

        Makes an SBOM public.

        Args:
            identity (str): identity of application

        Returns:
            :class:`Application` instance

        """
        LOGGER.debug("Regenerate %s", identity)
        return Application(
            **self._archivist.post(
                f"{self._subpath}/{identity}:{APPLICATIONS_REGENERATE}",
                None,
            )
        )
