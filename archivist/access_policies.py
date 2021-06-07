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
          "https://rkvst.poc.jitsuin.io",
          auth=authtoken,
      )
      asset = arch.access_policies.create(...)

"""

from copy import deepcopy

from .constants import (
    SEP,
    ACCESS_POLICIES_SUBPATH,
    ACCESS_POLICIES_LABEL,
    ASSETS_LABEL,
)

from .assets import Asset

DEFAULT_PAGE_SIZE = 500


class _AccessPoliciesClient:
    """AccessPoliciesClient

    Access to access_policies entitiies using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist):
        self._archivist = archivist

    def create(self, props, filters, access_permissions):
        """Create access policy

        Creates access policy with defined attributes.

        Args:
            props (dict): properties of created access policy.
            filters (list): assets filters
            access permissions (list): list of access permissions

        Returns:
            :class:`AccessPolicy` instance

        """
        return self.create_from_data(
            self.__query(props, filters=filters, access_permissions=access_permissions),
        )

    def create_from_data(self, data):
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

    def read(self, identity):
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

    def update(self, identity, props=None, filters=None, access_permissions=None):
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

    def delete(self, identity):
        """Delete Access Policy

        Deletes access policy.

        Args:
            identity (str): access_policies identity e.g. access_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`AccessPolicy` instance - empty?

        """
        return self._archivist.delete(ACCESS_POLICIES_SUBPATH, identity)

    @staticmethod
    def __query(props, *, filters=None, access_permissions=None):
        query = deepcopy(props) if props else {}
        if filters is not None:
            query["filters"] = filters

        if access_permissions is not None:
            query["access_permissions"] = access_permissions

        return query

    def count(self, *, display_name=None):
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
        self,
        *,
        page_size=DEFAULT_PAGE_SIZE,
        display_name=None,
    ):
        """List access policies.

        List access policiess that match criteria.

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
    def count_matching_assets(self, access_policy_id):
        """Count assets that match access_policy.

        Counts number of assets that match an access_polocy.

        Args:
            access_policy_id (str): e.g. access_policies/xxxxxxxxxxxxxxx

        Returns:
            integer count of assets.

        """
        return self._archivist.count(
            SEP.join((ACCESS_POLICIES_SUBPATH, access_policy_id, ASSETS_LABEL)),
        )

    def list_matching_assets(
        self,
        access_policy_id,
        *,
        page_size=DEFAULT_PAGE_SIZE,
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

    def count_matching_access_policies(self, asset_id):
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

    def list_matching_access_policies(self, asset_id, *, page_size=DEFAULT_PAGE_SIZE):
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


class AccessPolicy(dict):
    """AccessPolicy object"""
