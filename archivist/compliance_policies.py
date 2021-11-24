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
          "https://rkvst.poc.jitsuin.io",
          authtoken,
      )

      # A 'Since' policy
      asset = arch.compliance_policies.create(
          ComplianceTypeSince(...)
      )

"""

from copy import deepcopy
import logging
from typing import Dict, Optional, Union

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper

from .compliance_policy_requests import (
    CompliancePolicySince,
    CompliancePolicyCurrentOutstanding,
    CompliancePolicyPeriodOutstanding,
    CompliancePolicyDynamicTolerance,
    CompliancePolicyRichness,
)
from .compliance_policy_type import CompliancePolicyType
from .constants import (
    COMPLIANCE_POLICIES_SUBPATH,
    COMPLIANCE_POLICIES_LABEL,
)
from .dictmerge import _deepmerge

FIXTURE_LABEL = "compliance_policies"


LOGGER = logging.getLogger(__name__)


class CompliancePolicy(dict):
    """CompliancePolicy

    CompliancePolicy object has dictionary of all the compliance policy attributes.

    """

    @property
    def name(self):
        """str: name of the compliance policy"""
        try:
            name = self["display_name"]
        except (KeyError, TypeError):
            pass
        else:
            return name

        return None


class _CompliancePoliciesClient:
    """CompliancePoliciesClient

    Access to compliance policy entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

    def create(
        self,
        policy: Union[
            CompliancePolicySince,
            CompliancePolicyCurrentOutstanding,
            CompliancePolicyPeriodOutstanding,
            CompliancePolicyDynamicTolerance,
            CompliancePolicyRichness,
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

    def create_from_data(self, data: Dict) -> CompliancePolicy:
        """Create compliance_policy

        Creates compliance_policy with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of compliance_policy.

        Returns:
            :class:`CompliancePolicy` instance

        """
        return CompliancePolicy(
            **self._archivist.post(
                f"{COMPLIANCE_POLICIES_SUBPATH}/{COMPLIANCE_POLICIES_LABEL}",
                data,
            )
        )

    def read(self, identity: str) -> CompliancePolicy:
        """Read compliance policy

        Reads compliance policy.

        Args:
            identity (str): compliance policy identity
                            e.g. compliance_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`CompliancePolicy` instance

        """
        return CompliancePolicy(
            **self._archivist.get(COMPLIANCE_POLICIES_SUBPATH, identity)
        )

    def delete(self, identity: str) -> Dict:
        """Delete Compliance Policy

        Deletes compliance policy.

        Args:
            identity (str): compliance policy identity
            e.g. compliance_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`CompliancePolicy` instance - empty?

        """
        return self._archivist.delete(COMPLIANCE_POLICIES_SUBPATH, identity)

    def __query(self, props: Optional[Dict]) -> Dict:
        query = deepcopy(props) if props else {}
        # pylint: disable=protected-access
        return _deepmerge(self._archivist.fixtures.get(FIXTURE_LABEL), query)

    def count(self, *, props: Optional[Dict] = None) -> int:
        """Count compliance policies.

        Counts number of compliance policies that match criteria.

        Args:
            props (dict): e.g. {"display_name": "foo" }

        Returns:
            integer count of compliance policies.

        """
        return self._archivist.count(
            f"{COMPLIANCE_POLICIES_SUBPATH}/{COMPLIANCE_POLICIES_LABEL}",
            query=self.__query(props),
        )

    def list(self, *, page_size: Optional[int] = None, props: Dict = None):
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
                f"{COMPLIANCE_POLICIES_SUBPATH}/{COMPLIANCE_POLICIES_LABEL}",
                COMPLIANCE_POLICIES_LABEL,
                page_size=page_size,
                query=self.__query(props),
            )
        )

    def read_by_signature(self, *, props: Dict = None):
        """Read compliance policy by signature.

        Reads compliance policy that meets criteria. Only one compliance policy is expected.

        Args:
            props (dict): e.g. {"display_name": "foo" }

        Returns:
            :class:`CompliancePolicy` instance

        """
        return CompliancePolicy(
            **self._archivist.get_by_signature(
                f"{COMPLIANCE_POLICIES_SUBPATH}/{COMPLIANCE_POLICIES_LABEL}",
                COMPLIANCE_POLICIES_LABEL,
                query=self.__query(props),
            )
        )
