"""Assets interface

   Access to the assets endpoint.

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
      asset = arch.assets.create(...)

"""

from copy import deepcopy

from .constants import (
    ASSETS_SUBPATH,
    ASSETS_LABEL,
)
from .confirm import wait_for_confirmation, wait_for_confirmed


#: Default page size - number of entities fetched in one call to the
#: :func:`~_AssetsClient.list` method.
DEFAULT_PAGE_SIZE = 500


class _AssetsClient:
    """AssetsClient

    Access to assets entitiies using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist):
        self._archivist = archivist

    def create(self, behaviours, attrs, *, confirm=False):
        """Create asset

        Creates asset with defined behaviours and attributes.

        Args:
            behaviours (list): list of accepted behaviours for this asset.
            attrs (dict): attributes of created asset.
            confirm (bool): if True wait for asset to be confirmed on DLT.

        Returns:
            :class:`Asset` instance

        """
        return self.create_from_data(
            {
                "behaviours": behaviours,
                "attributes": attrs,
            },
            confirm=confirm,
        )

    def create_from_data(self, data, *, confirm=False):
        """Create asset

        Creates asset with request body from data stream.
        Suitable for reading data from a file using json.load or yaml.load

        Args:
            data (dict): request bosy of asset.
            confirm (bool): if True wait for asset to be confirmed on DLT.

        Returns:
            :class:`Asset` instance

        """
        asset = Asset(
            **self._archivist.post(
                f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
                data,
            )
        )
        if not confirm:
            return asset

        return wait_for_confirmation(self, asset["identity"])

    def read(self, identity):
        """Read asset

        Reads asset.

        Args:
            identity (str): assets identity e.g. assets/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            :class:`Asset` instance

        """
        return Asset(**self._archivist.get(ASSETS_SUBPATH, identity))

    @staticmethod
    def __query(props, attrs):
        query = deepcopy(props) if props else {}
        if attrs:
            query["attributes"] = attrs

        return query

    def count(self, *, props=None, attrs=None):
        """Count assets.

        Counts number of assets that match criteria.

        Args:
            props (dict): e.g. {"confirmation_status": "CONFIRMED" }
            attrs (dict): e.g. {"arc_display_type": "door" }

        Returns:
            integer count of assets.

        """
        return self._archivist.count(
            f"{ASSETS_SUBPATH}/{ASSETS_LABEL}", query=self.__query(props, attrs)
        )

    def wait_for_confirmed(self, *, props=None, attrs=None):
        """Wait for assets to be confirmed.

        Waits for all assets that match criteria to be confirmed.

        Args:
            props (dict): e.g. {"tracked": "TRACKED" }
            attrs (dict): e.g. {"arc_display_type": "door" }

        Returns:
            True if all assets are confirmed.

        """
        return wait_for_confirmed(self, props=props, attrs=attrs)

    def list(self, *, page_size=DEFAULT_PAGE_SIZE, props=None, attrs=None):
        """List assets.

        Lists assets that match criteria.

        Args:
            props (dict): optional e.g. {"tracked": "TRACKED" }
            attrs (dict): optional e.g. {"arc_display_type": "door" }
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`Asset` instances

        """
        return (
            Asset(**a)
            for a in self._archivist.list(
                f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
                ASSETS_LABEL,
                page_size=page_size,
                query=self.__query(props, attrs),
            )
        )

    def read_by_signature(self, *, props=None, attrs=None):
        """Read Asset by signature.

        Reads asset that meets criteria. Only one asset is expected.

        Args:
            props (dict): e.g. {"tracked": "TRACKED" }
            attrs (dict): e.g. {"arc_display_type": "door" }

        Returns:
            :class:`Asset` instance

        """
        return Asset(
            **self._archivist.get_by_signature(
                f"{ASSETS_SUBPATH}/{ASSETS_LABEL}",
                ASSETS_LABEL,
                query=self.__query(props, attrs),
            )
        )


class Asset(dict):
    """Asset

    Asset object has dictionary attributes and properties.

    """

    @property
    def primary_image(self):
        """Primary Image

        Attachment that is the primary image of the asset.

        Returns:
            :class:`Attachment` instance

        """
        try:
            attachments = self["attributes"]["arc_attachments"]
        except (KeyError, TypeError):
            pass
        else:
            return next(  # pragma: no cover
                (
                    a
                    for a in attachments
                    if "arc_display_name" in a
                    if a["arc_display_name"] == "arc_primary_image"
                ),
                None,
            )

        return None

    @property
    def name(self):
        """str: name of the asset"""
        try:
            name = self["attributes"]["arc_display_name"]
        except (KeyError, TypeError):
            pass
        else:
            return name

        return None
