"""Compliance Policies interface

   Access to the compliance_policies endpoint.

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

      # A 'Since' policy
      asset = arch.compliance_policies.create(
          ComplianceTypeSince(...)
      )

"""


from copy import deepcopy
from logging import getLogger
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    # pylint:disable=cyclic-import      # but pylint doesn't understand this feature
    from .archivist import Archivist
    from .compliance_policy_requests import (
        CompliancePolicyCurrentOutstanding,
        CompliancePolicyDynamicTolerance,
        CompliancePolicyPeriodOutstanding,
        CompliancePolicyRichness,
        CompliancePolicySince,
    )

from .constants import (
    COMPLIANCE_POLICIES_LABEL,
    COMPLIANCE_POLICIES_SUBPATH,
)
from .dictmerge import _deepmerge

LOGGER = getLogger(__name__)


class CompliancePolicy(dict):
    """CompliancePolicy

    CompliancePolicy object has dictionary of all the compliance policy attributes.

    """

    @property
    def name(self):
        """str: name of the compliance policy"""
        return self.get("display_name")


class _CompliancePoliciesClient:
    """CompliancePoliciesClient

    Access to compliance policy entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance
        self._subpath = f"{archivist_instance.root}/{COMPLIANCE_POLICIES_SUBPATH}"
        self._label = f"{self._subpath}/{COMPLIANCE_POLICIES_LABEL}"

    def __str__(self) -> str:
        return f"CompliancePoliciesClient({self._archivist.url})"

    def create(
        self,
        policy: Union[
            "CompliancePolicySince",
            "CompliancePolicyCurrentOutstanding",
            "CompliancePolicyPeriodOutstanding",
            "CompliancePolicyDynamicTolerance",
            "CompliancePolicyRichness",
        ],
    ) -> CompliancePolicy:
        """Create A compliance policy

        Args:
            policy (CompliancePolicy): the policy object.
            One of:
                CompliancePolicySince
                CompliancePolicyCurrentOutstanding
                CompliancePolicyPeriodOutstanding
                CompliancePolicyDynamicTolerance
                CompliancePolicyRichness

        Returns:
            :class:`CompliancePolicy` instance

        """
        return self.create_from_data(policy.dict())

    def create_from_data(self, data: "dict[str, Any]") -> "CompliancePolicy":
        """Create compliance_policy

        Creates compliance_policy with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of compliance_policy.

        Returns:
            :class:`CompliancePolicy` instance

        """
        return CompliancePolicy(**self._archivist.post(self._label, data))

    def read(self, identity: str) -> CompliancePolicy:
        """Read compliance policy

        Reads compliance policy.

        Args:
            identity (str): compliance policy identity
                            e.g. compliance_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`CompliancePolicy` instance

        """
        return CompliancePolicy(**self._archivist.get(f"{self._subpath}/{identity}"))

    def delete(self, identity: str) -> "dict[str, Any]":
        """Delete Compliance Policy

        Deletes compliance policy.

        Args:
            identity (str): compliance policy identity
            e.g. compliance_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`CompliancePolicy` instance - empty?

        """
        return self._archivist.delete(f"{self._subpath}/{identity}")

    def __params(self, props: "dict[str, Any]|None") -> "dict[str, Any]":
        params = deepcopy(props) if props else {}
        # pylint: disable=protected-access
        return _deepmerge(
            self._archivist.fixtures.get(COMPLIANCE_POLICIES_LABEL), params
        )

    def count(self, *, props: "dict[str, Any]|None" = None) -> int:
        """Count compliance policies.

        Counts number of compliance policies that match criteria.

        Args:
            props (dict): e.g. {"compliance_type": "COMPLIANCE_RICHNESS" }

        Returns:
            integer count of compliance policies.

        """
        return self._archivist.count(
            self._label,
            params=self.__params(props),
        )

    def list(
        self, *, page_size: "int|None" = None, props: "dict[str, Any]|None" = None
    ):
        """List compliance policies.

        Lists compliance policies that match criteria.

        Args:
            props (dict): optional e.g. {"compliance_type": "COMPLIANCE_DYNAMIC_TOLERANCE" }
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`CompliancePolicy` instances

        """
        return (
            CompliancePolicy(**a)
            for a in self._archivist.list(
                self._label,
                COMPLIANCE_POLICIES_LABEL,
                page_size=page_size,
                params=self.__params(props),
            )
        )

    def read_by_signature(self, *, props: "dict[str, Any]|None" = None):
        """Read compliance policy by signature.

        Reads compliance policy that meets criteria. Only one compliance policy is expected.

        Args:
            props (dict): e.g. {"display_name": "foo" }

        Returns:
            :class:`CompliancePolicy` instance

        """
        return CompliancePolicy(
            **self._archivist.get_by_signature(
                self._label,
                COMPLIANCE_POLICIES_LABEL,
                params=self.__params(props),
            )
        )
