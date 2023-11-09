"""Tenancies interface

   Access to the tenancies endpoint.

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
      tenancy = arch.tenancies.read(...)

"""


from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint:disable=cyclic-import      # but pylint doesn't understand this feature
    from .archivist import Archivist

from .constants import (
    TENANCIES_LABEL,
    TENANCIES_PREFIX,
    TENANCIES_SUBPATH,
)

LOGGER = getLogger(__name__)


class Tenant(dict):
    """Tenant object"""


class _TenanciesClient:
    """TenanciesClient

    Access to tenants entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    maxDiff = None

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance
        self._subpath = f"{archivist_instance.root}/{TENANCIES_SUBPATH}"
        self._label = f"{self._subpath}/{TENANCIES_LABEL}"

    def __str__(self) -> str:
        return f"TenanciesClient({self._archivist.url})"

    def _identity(self, identity) -> str:
        """Returns identity suitable for endpoint"""
        prefix, uuid = identity.split("/")
        if prefix == TENANCIES_PREFIX:
            return "/".join((TENANCIES_LABEL, uuid))

        return identity

    def publicinfo(self, identity: str) -> Tenant:
        """Read Tenant public info

        Reads Tenant public info

        Args:
            identity (str): tenancies identity e.g. tenancies/xxxxxxxxxxxxxxxxxxxxxxx
                                                 or tenant/xxxxxxxxxxxxxxxxxxxxxxx

        The tenant identity returned by most endpoints has the prefix 'tenant/'.
        However the tenancies endpoint expects 'tenancies/'. This is a wart in the
        archivist API and will be fixed at some future date.

        Returns:
            :class:`Tenant` instance

        """
        return Tenant(
            **self._archivist.get(
                f"{self._subpath}/{self._identity(identity)}:publicinfo"
            )
        )
