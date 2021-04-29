"""access_policies interface

   NOT TESTED
"""

from .constants import (
    SEP,
    ACCESS_POLICIES_SUBPATH,
    ACCESS_POLICIES_LABEL,
    ASSETS_LABEL,
)

DEFAULT_PAGE_SIZE=500


class _AccessPoliciesClient:
    """docstring
    """
    def __init__(self, archivist):
        """docstring
        """
        self._archivist = archivist

    def create(self, request):
        """docstring
        """

        return AccessPolicy(**self._archivist.post(
            f"{ACCESS_POLICIES_SUBPATH}/{ACCESS_POLICIES_LABEL}",
            request,
        ))

    def read(self, identity):
        """docstring
        """
        return AccessPolicy(**self._archivist.get(
            ACCESS_POLICIES_SUBPATH,
            identity,
        ))

    def update(self, identity, request):
        """docstring
        """
        return AccessPolicy(**self._archivist.patch(
            ACCESS_POLICIES_SUBPATH,
            identity,
            request,
        ))

    def delete(self, identity):
        """docstring
        """
        return self._archivist.delete(ACCESS_POLICIES_SUBPATH, identity)

    @staticmethod
    def __query(props):
        """docstring
        """
        query = props or {}
        return query

    def count(self, *, query=None):
        """docstring
        """
        return self._archivist.count(
            f"{ACCESS_POLICIES_SUBPATH}/{ACCESS_POLICIES_LABEL}",
            query=self.__query(query)
        )

    def list(self, *, page_size=DEFAULT_PAGE_SIZE, query=None):
        """docstring
        """
        return (
            AccessPolicy(**a) for a in self._archivist.list(
                f"{ACCESS_POLICIES_SUBPATH}/{ACCESS_POLICIES_LABEL}",
                ACCESS_POLICIES_LABEL,
                page_size=page_size,
                query=self.__query(query)
            )
        )

    # additional queries on different endpoints
    def count_matching_assets(self, access_policy_id, *, query=None):
        """docstring
        """
        return self._archivist.count(
            SEP.join((ACCESS_POLICIES_SUBPATH, access_policy_id, ASSETS_LABEL)),
            ASSETS_LABEL,
            query=self.__query(query)
        )

    def list_matching_assets(self, access_policy_id, *, page_size=DEFAULT_PAGE_SIZE, query=None):
        """docstring
        """
        return (
            AccessPolicy(**a) for a in self._archivist.list(
                SEP.join((ACCESS_POLICIES_SUBPATH, access_policy_id, ASSETS_LABEL)),
                ASSETS_LABEL,
                page_size=page_size,
                query=self.__query(query)
            )
        )

    def count_matching_access_policies(self, asset_id, *, query=None):
        """docstring
        """
        return self._archivist.count(
            SEP.join((ACCESS_POLICIES_SUBPATH, asset_id, ACCESS_POLICIES_LABEL)),
            ACCESS_POLICIES_LABEL,
            query=self.__query(query)
        )

    def list_matching_access_policies(self, asset_id, *, page_size=DEFAULT_PAGE_SIZE, query=None):
        """docstring
        """
        return (
            AccessPolicy(**a) for a in self._archivist.list(
                SEP.join((ACCESS_POLICIES_SUBPATH, asset_id, ASSETS_LABEL)),
                ACCESS_POLICIES_LABEL,
                page_size=page_size,
                query=self.__query(query)
            )
        )


class AccessPolicy(dict):
    """AccessPolicy object
    """
