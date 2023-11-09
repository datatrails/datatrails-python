"""Locations interface

   Direct access to the locations endpoint.

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
      location = arch.locations.create(...)


"""


from contextlib import suppress
from copy import deepcopy
from logging import getLogger
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # pylint:disable=cyclic-import      # but pylint doesn't understand this feature
    from .archivist import Archivist

from .constants import LOCATIONS_LABEL, LOCATIONS_SUBPATH
from .dictmerge import _deepmerge
from .errors import ArchivistNotFoundError
from .utils import selector_signature

LOGGER = getLogger(__name__)


class Location(dict):
    """Location

    Location object has dictionary attributes.

    """

    @property
    def name(self) -> "str | None":
        """str: name of the location"""
        name = None
        with suppress(KeyError):
            name = self["display_name"]

        return name


class _LocationsClient:
    """LocationsClient

    Access to locations entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance
        self._subpath = f"{archivist_instance.root}/{LOCATIONS_SUBPATH}"
        self._label = f"{self._subpath}/{LOCATIONS_LABEL}"

    def __str__(self) -> str:
        return f"LocationsClient({self._archivist.url})"

    def create(
        self, props: "dict[str, Any]", *, attrs: "dict[str, Any]|None" = None
    ) -> Location:
        """Create location

        Creates location with defined properties and attributes.

        Args:
            props (dict): properties for this location.
            attrs (dict): attributes of created location.

        Returns:
            :class:`Location` instance

        """
        LOGGER.debug("Create Location %s", props)
        return self.create_from_data(self.__params(props, attrs))

    def create_from_data(self, data: "dict[str, Any]") -> Location:
        """Create location

        Creates location with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request body of location.

        Returns:
            :class:`Location` instance

        """
        return Location(**self._archivist.post(self._label, data))

    def create_if_not_exists(self, data: "dict[str, Any]") -> "tuple[Location, bool]":
        """
        Create a location if not already exists

        Args:
            data (dict): request body of location.

        A YAML representation of the data argument would be:

            .. code-block:: yaml

                selector:
                  - display_name
                  - attributes:
                    - wavestone_ext
                display_name: Apartements du Gare du Nord
                description: Residential apartment building in new complex above GdN station
                latitude: 48.8809
                longitude: 2.3553
                attributes:
                  address: 18 Rue de Dunkerque, 75010 Paris, France
                  wavestone_ext: managed

            The 'selector' setting is required.

        Returns:
            tuple of :class:`Location` instance, Boolean True if already exists

        """

        data = deepcopy(data)
        selector = data.pop("selector")  # must exist
        props, attrs = selector_signature(selector, data)
        try:
            location = self.read_by_signature(props=props, attrs=attrs)

        except ArchivistNotFoundError:
            LOGGER.info(
                "location with selector %s,%s does not exist - creating", props, attrs
            )

        else:
            LOGGER.info("location with selector %s,%s already exists", props, attrs)
            return location, True

        return self.create_from_data(data), False

    def read(self, identity: str) -> Location:
        """Read location

        Reads location.

        Args:
            identity (str): location identity e.g. locations/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Location` instance

        """
        return Location(**self._archivist.get(f"{self._subpath}/{identity}"))

    def __params(
        self, props: "dict[str, Any]|None", attrs: "dict[str, Any]|None"
    ) -> "dict[str, Any]":
        params = deepcopy(props) if props else {}
        if attrs:
            params["attributes"] = attrs

        return _deepmerge(self._archivist.fixtures.get(LOCATIONS_LABEL), params)

    def count(
        self,
        *,
        props: "dict[str, Any]|None" = None,
        attrs: "dict[str, Any]|None" = None,
    ) -> int:
        """Count locations.

        Counts number of locations that match criteria.

        Args:
            props (dict): e.g. {"display_name": "Macclesfield" }
            attrs (dict): e.g. {"director": "john smith" }

        Returns:
            integer count of locations.

        """
        return self._archivist.count(self._label, params=self.__params(props, attrs))

    def list(
        self,
        *,
        page_size: "int|None" = None,
        props: "dict[str, Any]|None" = None,
        attrs: "dict[str, Any]|None" = None,
    ):
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
                self._label,
                LOCATIONS_LABEL,
                page_size=page_size,
                params=self.__params(props, attrs),
            )
        )

    def read_by_signature(
        self,
        *,
        props: "dict[str, Any]|None" = None,
        attrs: "dict[str, Any]|None" = None,
    ) -> Location:
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
                self._label,
                LOCATIONS_LABEL,
                params=self.__params(props, attrs),
            )
        )
