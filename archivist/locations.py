"""Locations interface

   Direct access to the locations endpoint.

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
      location = arch.locations.create(...)


"""

from .constants import LOCATIONS_SUBPATH, LOCATIONS_LABEL


#: Default page size - number of entities fetched in one call to the
#: :func:`~_LocationsClient.list` method.
DEFAULT_PAGE_SIZE = 500


class _LocationsClient:
    """LocationsClient

    Access to locations entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist):
        self._archivist = archivist

    def create(self, props, *, attrs=None):
        """Create location

        Creates location with defined properties and attributes.

        Args:
            props (dict): properties for this location.
            attrs (dict): attributes of created location.

        Returns:
            :class:`Location` instance

        """
        return self.create_from_data(self.__query(props, attrs))

    def create_from_data(self, data):
        """Create location

        Creates location with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of location.

        Returns:
            :class:`Location` instance

        """
        return Location(
            **self._archivist.post(
                f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}",
                data,
            )
        )

    def read(self, identity):
        """Read location

        Reads location.

        Args:
            identity (str): location identity e.g. locations/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Location` instance

        """
        return Location(
            **self._archivist.get(
                LOCATIONS_SUBPATH,
                identity,
            )
        )

    @staticmethod
    def __query(props, attrs):
        query = props or {}
        if attrs:
            query["attributes"] = attrs

        return query

    def count(self, *, props=None, attrs=None):
        """Count locations.

        Counts number of locations that match criteria.

        Args:
            props (dict): e.g. {"display_name": "Macclesfield" }
            attrs (dict): e.g. {"director": "john smith" }

        Returns:
            integer count of locations.

        """
        return self._archivist.count(
            f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}", query=self.__query(props, attrs)
        )

    def list(self, *, page_size=DEFAULT_PAGE_SIZE, props=None, attrs=None):
        """List locations.

        Lists locations that match criteria.

        Args:
            props (dict): optional e.g. {"display_name": "Macclesfield" }
            attrs (dict): optional e.g. {"director": "john smith" }
            page_size (int): optional page size. (Rarely used)

        Returns:
            iterable that returns :class:`Location` instances

        """

        return (
            Location(**a)
            for a in self._archivist.list(
                f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}",
                LOCATIONS_LABEL,
                page_size=page_size,
                query=self.__query(props, attrs),
            )
        )

    def read_by_signature(self, *, props=None, attrs=None):
        """Read location by signature.

        Reads location that meets criteria. Only one location is expected.

        Args:
            props (dict): e.g. {"display_name": "Macclesfield" }
            attrs (dict): e.g. {"director": "john smith" }

        Returns:
            :class:`Location` instance

        """
        return Location(
            **self._archivist.get_by_signature(
                f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}",
                LOCATIONS_LABEL,
                query=self.__query(props, attrs),
            )
        )


class Location(dict):
    """Location

    Location object has dictionary attributes.

    """
