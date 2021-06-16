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
          auth=authtoken,
      )
      asset = arch.compliance_policies.create(...)

"""

from copy import deepcopy
from enum import Enum

from .constants import (
    COMPLIANCE_POLICIES_SUBPATH,
    COMPLIANCE_POLICIES_LABEL,
)


#: Default page size - number of entities fetched in one call to the
#: :func:`~_AssetsClient.list` method.
DEFAULT_PAGE_SIZE = 500


class PolicyType(Enum):
    """PolicyType

    PolicyType is the type of compliance policy
    """

    COMPLIANCE_TYPE_UNDEFINED = 1
    COMPLIANCE_SINCE = 2
    COMPLIANCE_CURRENT_OUTSTANDING = 3
    COMPLIANCE_PERIOD_OUTSTANDING = 4
    COMPLIANCE_DYNAMIC_TOLERANCE = 5
    COMPLIANCE_RICHNESS = 6


class _CompliancePoliciesClient:
    """CompliancePoliciesClient

    Access to compliance policy entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist):
        self._archivist = archivist

    def create(self, description, display_name, asset_filter,
               compliance_type=PolicyType.COMPLIANCE_TYPE_UNDEFINED,
               richness_assertions=None, event_display_type="", closing_event_display_type="",
               time_period_seconds=0, dynamic_window=0, dynamic_variability=0.0):
        """Create compliance policy

        Args:
            description (string): the policy description.
            display_name (string): the policy non-unique name.
            asset_filter (filter): in the form [{"or":["identity=foo",...],...}]
            compliance_type (PolicyType): policy type, default to `TYPE_UNDEFINED`.
            richness_assertions (filter): format [{"or":["foo<7",...]}...] required for RICHNESS
            event_display_type (string): target event display type (not needed for richness)
            closing_event_display_type (string): closing event display type.
            time_period_seconds (int):  time delta - required for SINCE and PERIOD_OUTSTANDING
            dynamic_window (int): valid period for policy - required for DYNAMIC_TOLERANCE
            dynamic_variability (float): % of stddevs allowed, required for DYNAMIC_TOLERANCE

        Returns:
            :class:`CompliancePolicy` instance

        """
        #pylint: disable=too-many-arguments

        data = self.create_from_data(
            {
                "compliance_type": compliance_type.name,  # get the name of the enum
                "description": description,
                "display_name": display_name,
                "asset_filter": asset_filter,
                "event_display_type": event_display_type,
                "closing_event_display_type": closing_event_display_type,
                "time_period_seconds": time_period_seconds,
                "dynamic_window": dynamic_window,
                "dynamic_variability": dynamic_variability,
            },
        )

        if richness_assertions is not None:
            data["richness_assertions"] = richness_assertions

        return data

    def create_from_data(self, data):
        """Create compliance_policy

        Creates compliance_policy with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request bosy of compliance_policy.

        Returns:
            :class:`CompliancePolicy` instance

        """
        compliance_policy = CompliancePolicy(
            **self._archivist.post(
                f"{COMPLIANCE_POLICIES_SUBPATH}/{COMPLIANCE_POLICIES_LABEL}",
                data,
            )
        )

        return compliance_policy

    def delete(self, identity):
        """Delete Compliance Policy

        Deletes compliance policy.

        Args:
            identity (str): subjects identity e.g. compliance_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`CompliancePolicy` instance - empty?

        """
        return self._archivist.delete(COMPLIANCE_POLICIES_SUBPATH, identity)

    def read(self, identity):
        """Read compliance policy

        Reads compliance policy.

        Args:
            identity (str): compliance policy id e.g. compliance_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`CompliancePolicy` instance

        """
        return CompliancePolicy(**self._archivist.get(COMPLIANCE_POLICIES_SUBPATH, identity))

    @staticmethod
    def __query(props):
        query = deepcopy(props) if props else {}
        return query

    def count(self, *, props=None):
        """Count compliance policies.

        Counts number of compliance policies that match criteria.

        Args:
            props (dict): e.g. {"display_name": "foo" }

        Returns:
            integer count of compliance policies.

        """
        return self._archivist.count(
            f"{COMPLIANCE_POLICIES_SUBPATH}/{COMPLIANCE_POLICIES_LABEL}", query=self.__query(props)
        )

    def list(self, *, page_size=DEFAULT_PAGE_SIZE, props=None):
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

    def read_by_signature(self, *, props=None):
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
