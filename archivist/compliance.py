"""Compliance interface

   Access to the compliance endpoint.

   The user is not expected to use this class directly. It is an attribute of the
   :class:`Archivist` class.

   For example instantiate an Archivist instance and execute the methods of the class:

   .. code-block:: python

      with open(".auth_token", mode="r") as tokenfile:
          authtoken = tokenfile.read().strip()

      # Initialize connection to Archivist
      arch = Archivist(
          "https://rkvst.poc.jitsuin.io",
          auth=authtoken,
      )
      asset = arch.compliance.read(...)

"""

from copy import deepcopy
from enum import Enum
from types import SimpleNamespace

from .constants import (
    COMPLIANCE_SUBPATH,
    COMPLIANCE_LABEL,
)


#: Default page size - number of entities fetched in one call to the
#: :func:`~_AssetsClient.list` method.
DEFAULT_PAGE_SIZE = 500


class _ComplianceClient:
    """ComplianceClient

    Access to compliance entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist):
        self._archivist = archivist

    def read(self, identity, complaint_at=None):
        """Read compliance

        Reads compliance of a particular asset.

        Args:
            identity (str): asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxx
            compliant_at (str): datetime to check compliance at a particular time (optional).
                                format: https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html#rfc.section.5.6

        Returns:
            :class:`Compliance` instance

        """
        return Compliance(**self._archivist.get(f"{COMPLIANCE_SUBPATH}/{COMPLIANCE_LABEL}", identity,
                          params={"compliant_at": complaint_at}))


class Compliance(dict):
    """Compliance

    Compliance object has dictionary of all the compliance attributes.

    """
