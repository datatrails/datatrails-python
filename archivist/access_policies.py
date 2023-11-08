"""Access_Policies interface

   Access to the access_policies endpoint.

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
      access_policy = arch.access_policies.create(...)

"""

from copy import deepcopy
from logging import getLogger
from typing import TYPE_CHECKING, Any, Generator

# pylint:disable=cyclic-import      # but pylint doesn't understand this feature

if TYPE_CHECKING:
    from .archivist import Archivist

from .assets import Asset
from .constants import (
    ACCESS_POLICIES_LABEL,
    ACCESS_POLICIES_SUBPATH,
    ASSETS_LABEL,
)
from .dictmerge import _deepmerge

LOGGER = getLogger(__name__)


class AccessPolicy(dict):
    """AccessPolicy object"""

    @property
    def name(self) -> "str | None":
        """str: name of the access policy"""
        return self.get("display_name")


class _AccessPoliciesClient:
    """AccessPoliciesClient

    Access to access_policies entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance
        self._subpath = f"{archivist_instance.root}/{ACCESS_POLICIES_SUBPATH}"
        self._label = f"{self._subpath}/{ACCESS_POLICIES_LABEL}"

    def __str__(self) -> str:
        return f"AccessPoliciesClient({self._archivist.url})"

    def create(
        self,
        props: "dict[str, Any]",
        filters: "list[dict[str, Any]]",
        access_permissions: "list[dict[str, Any]]",
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
            self.__params(
                props, filters=filters, access_permissions=access_permissions
            ),
        )

    def create_from_data(self, data: "dict[str, Any]") -> AccessPolicy:
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
                f"{self._subpath}/{ACCESS_POLICIES_LABEL}",
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
        return AccessPolicy(**self._archivist.get(f"{self._subpath}/{identity}"))

    def update(
        self,
        identity,
        *,
        props: "dict[str, Any] | None " = None,
        filters: "list[dict] | None " = None,
        access_permissions: "list[dict] | None " = None,
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
                f"{self._subpath}/{identity}",
                self.__params(
                    props, filters=filters, access_permissions=access_permissions
                ),
            )
        )

    def delete(self, identity: str) -> "dict[str, Any]":
        """Delete Access Policy

        Deletes access policy.

        Args:
            identity (str): access_policies identity e.g. access_policies/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`AccessPolicy` instance - empty?

        """
        return self._archivist.delete(f"{self._subpath}/{identity}")

    def __params(
        self,
        props: "dict[str, Any] | None",
        *,
        filters: "list[dict] | None" = None,
        access_permissions: "list[dict] | None" = None,
    ) -> "dict[str, Any]":
        params = deepcopy(props) if props else {}
        if filters is not None:
            params["filters"] = filters

        if access_permissions is not None:
            params["access_permissions"] = access_permissions

        return _deepmerge(self._archivist.fixtures.get(ACCESS_POLICIES_LABEL), params)

    def count(self, *, display_name: "str | None" = None) -> int:
        """Count access policies.

        Counts number of access policies that match criteria.

        Args:
            display_name (str): display name (optional0

        Returns:
            integer count of access policies.

        """
        params = {"display_name": display_name} if display_name is not None else None
        return self._archivist.count(self._label, params=params)

    def list(
        self, *, page_size: "int|None" = None, display_name: "str|None" = None
    ) -> Generator[AccessPolicy, None, None]:
        """List access policies.

        List access policies that match criteria.

        Args:
            display_name (str): display name (optional0
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`AccessPolicy` instances

        """
        params = {"display_name": display_name} if display_name is not None else None
        return (
            AccessPolicy(**a)
            for a in self._archivist.list(
                self._label,
                ACCESS_POLICIES_LABEL,
                page_size=page_size,
                params=params,
            )
        )

    # additional queries on different endpoints
    def list_matching_assets(
        self, access_policy_id: str, *, page_size: "int|None" = None
    ) -> Generator[Asset, None, None]:
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
                f"{self._subpath}/{access_policy_id}/{ASSETS_LABEL}",
                ASSETS_LABEL,
                page_size=page_size,
            )
        )

    def list_matching_access_policies(
        self, asset_id: str, *, page_size: "int|None" = None
    ) -> Generator[AccessPolicy, None, None]:
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
                f"{self._subpath}/{asset_id}/{ACCESS_POLICIES_LABEL}",
                ACCESS_POLICIES_LABEL,
                page_size=page_size,
            )
        )
