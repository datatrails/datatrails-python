"""Appidp interface

   Access to the Appidp endpoint.

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
      appidp = arch.appidp.token(...)

"""

from __future__ import annotations
from logging import getLogger

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
# pylint:disable=too-few-public-methods
from . import archivist

from .constants import (
    APPIDP_SUBPATH,
    APPIDP_LABEL,
    APPIDP_TOKEN,
)

LOGGER = getLogger(__name__)


class AppIDP(dict):
    """Appidp object"""


class _AppIDPClient:
    """AppIDP Client

    Access to appidp entities. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: archivist.Archivist):
        self._archivist = archivist_instance
        self._subpath = f"{archivist_instance.root}/{APPIDP_SUBPATH}"
        self._label = f"{self._subpath}/{APPIDP_LABEL}"

    def __str__(self) -> str:
        return f"AppIDPClient({self._archivist.url})"

    def token(self, client_id: str, client_secret: str) -> AppIDP:
        """Create access token from client id and secret

        Args:
            client_id (str): client id
            client_secret (str): client_secret

        Returns:
            :class:`AppIDP` instance

        """
        return AppIDP(
            **self._archivist.post(
                f"{self._label}/{APPIDP_TOKEN}",
                {
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                data=True,
            )
        )
