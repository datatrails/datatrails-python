"""locations interface


"""

from .constants import LOCATIONS_SUBPATH, LOCATIONS_LABEL

DEFAULT_PAGE_SIZE=500


class _LocationsClient:
    """docstring
    """
    def __init__(self, archivist):
        """docstring
        """
        self._archivist = archivist

    def create(self, props, *, attrs=None):
        """docstring
        """
        return self.create_from_data(
            self.__query(props, attrs)
        )

    def create_from_data(self, data):
        """docstring

        read request from data stream
        """
        return Location(**self._archivist.post(
            f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}",
            data,
        ))

    def read(self, identity):
        """docstring
        """
        return Location(**self._archivist.get(
            LOCATIONS_SUBPATH,
            identity,
        ))

    @staticmethod
    def __query(props, attrs):
        """docstring
        """
        query = props or {}
        if attrs:
            query['attributes'] = attrs

        return query

    def count(self, *, props=None, attrs=None):
        """docstring
        """
        return self._archivist.count(
            f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}",
            query=self.__query(props, attrs)
        )

    def list(self, *, page_size=DEFAULT_PAGE_SIZE, props=None, attrs=None):
        """docstring
        """
        return (
            Location(**a) for a in self._archivist.list(
                f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}",
                LOCATIONS_LABEL,
                page_size=page_size,
                query=self.__query(props, attrs)
            )
        )

    def read_by_signature(self, *, props=None, attrs=None):
        """docstring
        """
        return Location(**self._archivist.get_by_signature(
            f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}",
            LOCATIONS_LABEL,
            query=self.__query(props, attrs)
        ))


class Location(dict):
    """Location object
    """
