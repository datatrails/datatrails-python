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
          "https://app.datatrails.ai",
          authtoken,
      )
      asset = arch.compliance.compliant_at(...)

"""


from logging import getLogger
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # pylint:disable=cyclic-import      # but pylint doesn't understand this feature
    from .archivist import Archivist

from .constants import (
    COMPLIANCE_LABEL,
    COMPLIANCE_SUBPATH,
)

LOGGER = getLogger(__name__)


class Compliance(dict):
    """Compliance

    Compliance object has dictionary of all the compliance attributes.

    """


# pylint: disable=too-few-public-methods
class _ComplianceClient:  # pylint: disable=too-few-public-methods
    """ComplianceClient

    Access to compliance entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance
        self._subpath = f"{archivist_instance.root}/{COMPLIANCE_SUBPATH}"
        self._label = f"{self._subpath}/{COMPLIANCE_LABEL}"

    def __str__(self) -> str:
        return f"ComplianceClient({self._archivist.url})"

    def compliant_at(
        self,
        asset_id,
        *,
        compliant_at: "bool|None" = None,
        report: "str|None" = None,
    ) -> Compliance:
        """
        Reads compliance of a particular asset.

        Args:
            asset_id (str): asset identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxx
            compliant_at (str): datetime to check compliance at a particular time (optional).
                                format: rfc3339 - UTC only
                                https://datatracker.ietf.org/doc/html/rfc3339#section-4.1
            report (bool): if true output report
            page_size (int): optional page size. (Rarely used).

        Returns:
            :class:`Compliance` instance

        """
        params = {"compliant_at": compliant_at} if compliant_at is not None else None
        response = self._archivist.get(
            f"{self._label}/{asset_id}",
            params=params,
        )
        if report is True:
            self.compliant_at_report(response)
        return Compliance(**response)

    def compliant_at_report(self, compliance: "dict[str, Any]"):
        """
        Prints report of compliance_at request

        Args:
            compliance (dict): compliance object encapsulating response from compliant_at
        """

        LOGGER.info("Compliant %s", compliance["compliant"])
        for outcome in compliance["compliance"]:
            if outcome["compliant"]:
                continue

            # get the compliance policy
            policy = self._archivist.compliance_policies.read(
                outcome["compliance_policy_identity"]
            )

            # print the policy name and the reason
            LOGGER.info(
                "NON-COMPLIANCE -> Policy: %s: Reason %s",
                policy["display_name"],
                outcome["reason"],
            )
