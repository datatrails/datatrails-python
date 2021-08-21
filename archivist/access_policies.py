"""Access_Policies interface

   Access to the access_policies endpoint.

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
      access_policy = arch.access_policies.create(...)

"""

from typing import Dict, List, Optional
import logging
from copy import deepcopy

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from archivist import archivist as type_helper

from .constants import (
    SEP,
    ACCESS_POLICIES_SUBPATH,
    ACCESS_POLICIES_LABEL,
    ASSETS_LABEL,
)
from .dictmerge import _deepmerge

from .assets import Asset

#: Default page size - number of entities fetched in one REST GET in the
#: :func:`~_AccessPoliciesClient.list` method. This can be overridden but should rarely
#: be changed.
DEFAULT_PAGE_SIZE = 500

FIXTURE_LABEL = "access_policies"


LOGGER = logging.getLogger(__name__)


class AccessPolicy(dict):
    """AccessPolicy object"""


class _AccessPoliciesClient:
    """AccessPoliciesClient

    Access to access_policies entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

    def create(
        self, props: Dict, filters: List, access_permissions: List
    ) -> AccessPolicy:
        """Create access policy

        Creates access policy with defined attributes.

        Args:
            props (dict): properties of created access policy.
            filters (list): assets filters
            access permissions (list): list of access permissions

        Returns:
            :class:`AccessPolicy` instance

        """
        LOGGER.debug("Create Access Policy %s", props)
        return self.create_from_data(
            self.__query(props, filters=filters, access_permissions=access_permissions),
        )

    def create_from_data(self, data: Dict) -> AccessPolicy:
        """Create access policy

        Creates access policy with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of access policy.

        Returns:
            :class:`AccessPolicy` instance

        """
        return AccessPolicy(
            **self._archivist.post(
                f"{ACCESS_POLICIES_SUBPATH}/{ACCESS_POLICIES_LABEL}",
                data,
            )
        )

    def read(self, identity: str) -> AccessPolicy:
        """Read Access Policy

        Reads access policy.

        Args:
            identity (str): access_policies identity e.g. access_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`AccessPolicy` instance

        """
        return AccessPolicy(
            **self._archivist.get(
                ACCESS_POLICIES_SUBPATH,
                identity,
            )
        )

    def update(
        self,
        identity,
        props: Optional[Dict] = None,
        filters: Optional[List] = None,
        access_permissions: Optional[List] = None,
    ) -> AccessPolicy:
        """Update Access Policy

        Update access policy.

        Args:
            identity (str): access_policies identity e.g. access_policies/xxxxxxxxxxxxxxxxxxxxxxx
            props (dict): properties of created access policy.
            filters (list): assets filters
            access permissions (list): list of access permissions

        Returns:
            :class:`AccessPolicy` instance

        """
        return AccessPolicy(
            **self._archivist.patch(
                ACCESS_POLICIES_SUBPATH,
                identity,
                self.__query(
                    props, filters=filters, access_permissions=access_permissions
                ),
            )
        )

    def delete(self, identity: str) -> Dict:
        """Delete Access Policy

        Deletes access policy.

        Args:
            identity (str): access_policies identity e.g. access_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`AccessPolicy` instance - empty?

        """
        return self._archivist.delete(ACCESS_POLICIES_SUBPATH, identity)

    def __query(
        self,
        props: Optional[Dict],
        *,
        filters: Optional[List] = None,
        access_permissions: Optional[List] = None,
    ) -> Dict:
        query = deepcopy(props) if props else {}
        if filters is not None:
            query["filters"] = filters

        if access_permissions is not None:
            query["access_permissions"] = access_permissions

        return _deepmerge(self._archivist.fixtures.get(FIXTURE_LABEL), query)

    def count(self, *, display_name: Optional[str] = None) -> int:
        """Count access policies.

        Counts number of access policies that match criteria.

        Args:
            display_name (str): display name (optional0

        Returns:
            integer count of access policies.

        """
        query = {"display_name": display_name} if display_name is not None else None
        return self._archivist.count(
            f"{ACCESS_POLICIES_SUBPATH}/{ACCESS_POLICIES_LABEL}",
            query=query,
        )

    def list(
        self, *, page_size: int = DEFAULT_PAGE_SIZE, display_name: Optional[str] = None
    ):
        """List access policies.

        List access policies that match criteria.

        Args:
            display_name (str): display name (optional0
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`AccessPolicy` instances

        """
        query = {"display_name": display_name} if display_name is not None else None
        return (
            AccessPolicy(**a)
            for a in self._archivist.list(
                f"{ACCESS_POLICIES_SUBPATH}/{ACCESS_POLICIES_LABEL}",
                ACCESS_POLICIES_LABEL,
                page_size=page_size,
                query=query,
            )
        )

    # additional queries on different endpoints
    def count_matching_assets(self, access_policy_id: str) -> int:
        """Count assets that match access_policy.

        Counts number of assets that match an access_policy.

        Args:
            access_policy_id (str): e.g. access_policies/xxxxxxxxxxxxxxx

        Returns:
            integer count of assets.

        """
        return self._archivist.count(
            SEP.join((ACCESS_POLICIES_SUBPATH, access_policy_id, ASSETS_LABEL)),
        )

    def list_matching_assets(
        self, access_policy_id: str, *, page_size: int = DEFAULT_PAGE_SIZE
    ):
        """List matching assets.

        List assets that match access policy.

        Args:
            access_policy_id (str): e.g. access_policies/xxxxxxxxxxxxxxx
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`Asset` instances

        """
        return (
            Asset(**a)
            for a in self._archivist.list(
                SEP.join((ACCESS_POLICIES_SUBPATH, access_policy_id, ASSETS_LABEL)),
                ASSETS_LABEL,
                page_size=page_size,
            )
        )

    def count_matching_access_policies(self, asset_id: str) -> int:
        """Count access policies that match asset.

        Counts number of access policies that match asset.

        Args:
            asset_id (str): e.g. assets/xxxxxxxxxxxxxxx

        Returns:
            integer count of access policies.

        """
        return self._archivist.count(
            SEP.join((ACCESS_POLICIES_SUBPATH, asset_id, ACCESS_POLICIES_LABEL)),
        )

    def list_matching_access_policies(
        self, asset_id: str, *, page_size: int = DEFAULT_PAGE_SIZE
    ):
        """List matching access policies.

        List access policies that match asset.

        Args:
            asset_id (str): e.g. assets/xxxxxxxxxxxxxxx
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`AccessPolicy` instances

        """
        return (
            AccessPolicy(**a)
            for a in self._archivist.list(
                SEP.join((ACCESS_POLICIES_SUBPATH, asset_id, ACCESS_POLICIES_LABEL)),
                ACCESS_POLICIES_LABEL,
                page_size=page_size,
            )
        )
