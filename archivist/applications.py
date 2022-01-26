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

from logging import getLogger
from typing import Dict, Optional

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper

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

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

    def __str__(self) -> str:
        return f"ApplicationsClient({self._archivist.url})"

    def create(self, display_name: str, custom_claims: Dict) -> Application:
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
            self.__query(
                display_name=display_name,
                custom_claims=custom_claims,
            ),
        )

    def create_from_data(self, data: Dict) -> Application:
        """Create application

        Creates application with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of application.

        Returns:
            :class:`Application` instance

        """
        return Application(
            **self._archivist.post(
                f"{APPLICATIONS_SUBPATH}/{APPLICATIONS_LABEL}",
                data,
            )
        )

    def read(self, identity: str) -> Application:
        """Read Application

        Reads application.

        Args:
            identity (str): applications identity e.g. applications/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Application` instance

        """
        return Application(
            **self._archivist.get(
                APPLICATIONS_SUBPATH,
                identity,
            )
        )

    def update(
        self,
        identity: str,
        *,
        display_name: str = None,
        custom_claims: Optional[Dict] = None,
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
                APPLICATIONS_SUBPATH,
                identity,
                self.__query(
                    display_name=display_name,
                    custom_claims=custom_claims,
                ),
            )
        )

    def delete(self, identity: str) -> Dict:
        """Delete Application

        Deletes application.

        Args:
            identity (str): applications identity e.g. applications/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Application` instance - empty?

        """
        return self._archivist.delete(APPLICATIONS_SUBPATH, identity)

    def __query(
        self,
        *,
        display_name: Optional[str] = None,
        custom_claims: Optional[Dict] = None,
    ) -> Dict:

        query = {}

        if display_name is not None:
            query["display_name"] = display_name

        if custom_claims is not None:
            query["custom_claims"] = custom_claims

        return _deepmerge(self._archivist.fixtures.get(APPLICATIONS_LABEL), query)

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
                f"{APPLICATIONS_SUBPATH}/{APPLICATIONS_LABEL}",
                APPLICATIONS_LABEL,
                page_size=page_size,
                query=self.__query(display_name=display_name),
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
                f"{APPLICATIONS_SUBPATH}/{identity}",
                None,
                verb=APPLICATIONS_REGENERATE,
            )
        )
