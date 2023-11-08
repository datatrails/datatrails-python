"""Attachments interface

   Direct access to the attachments endpoint

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
      with open("something.jpg") as fd:
          attachment = arch.attachments.upload(fd)

"""

# pylint:disable=too-few-public-methods


from copy import deepcopy
from logging import getLogger
from typing import TYPE_CHECKING, Any, BinaryIO
from urllib.parse import urlparse

if TYPE_CHECKING:
    from requests.models import Response

    # pylint:disable=cyclic-import      # but pylint doesn't understand this feature
    from .archivist import Archivist

from .constants import (
    ASSETATTACHMENTS_LABEL,
    ASSETATTACHMENTS_SUBPATH,
    ATTACHMENTS_LABEL,
    SEP,
)
from .dictmerge import _deepmerge

LOGGER = getLogger(__name__)


class _AssetAttachmentsClient:
    """AssetAttachmentsClient

    Access to attachments entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist_instance: "Archivist"):
        self._archivist = archivist_instance
        self._public = archivist_instance.public
        self._subpath = f"{archivist_instance.root}/{ASSETATTACHMENTS_SUBPATH}"
        self._label = f"{self._subpath}/{ASSETATTACHMENTS_LABEL}"

    def __str__(self) -> str:
        if self._public:
            return "AssetAttachmentsClient()"

        return f"AssetAttachmentsClient({self._archivist.url})"

    def _identity(self, identity: str, attachment_id: str) -> str:
        """Return fully qualified identity
        If public then expect a full url as argument

        identity looks like:

        [https://app.datatrails.ai/archivist/public]assets/xxxxxxx

        OR

        [https://app.datatrails.ai/archivist/public]assets/xxxxxxx/events/yyyyyy

        where the public URL is prefixed with the schema.

        """
        uuid = attachment_id.split(SEP)[1]
        if self._public:
            # the public URL for the asset or event has to be changed
            url = urlparse(identity)
            root = "/".join(url.path.split(SEP)[:2])
            asset_id = "/".join(url.path.split(SEP)[2:])
            new_url = url._replace(
                path=f"{root}/{ASSETATTACHMENTS_SUBPATH}/{ASSETATTACHMENTS_LABEL}/{asset_id}/{uuid}"
            )
            return new_url.geturl()

        return f"{self._label}/{identity}/{uuid}"

    def __params(self, params: "dict[str, Any]|None") -> "dict[str, Any]":
        params = deepcopy(params) if params else {}
        # pylint: disable=protected-access
        return _deepmerge(self._archivist.fixtures.get(ATTACHMENTS_LABEL), params)

    def download(
        self,
        identity: str,
        attachment_id: str,
        fd: BinaryIO,
        *,
        params: "dict[str, Any]|None" = None,
    ) -> "Response":
        """Read attachment

        Reads attachment into data sink (usually a file opened for write).
        Note that returns the response as the body will be consumed by the
        fd iterator

        Args:
            identity (str): identity
            attachment_id (str): blobs/aaaaaaaaaaaaa
            fd (file): opened file descriptor or other file-type sink.
            params (dict): e.g. {"allow_insecure": "true"} OR {"strict": "true" }

        Returns:
            JSON as dict

        identity has one of the following 4 forms:

            [https://app.datatrails.ai/archivist/][v2/] - if public
            assets/xxxxxxxxxxxxxxxxxxxxxxxxxx

            [https://app.datatrails.ai/archivist/][v2/] - if public
            assets/xxxxxxxxxxxxxxxxxxxxxxxxxx/events/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

        """

        return self._archivist.get_file(
            self._identity(identity, attachment_id), fd, params=self.__params(params)
        )

    def info(
        self,
        identity: str,
        attachment_id: str,
    ) -> "dict[str, Any]":
        """Read asset attachment info

        Reads asset attachment info

        Args:
            identity (str): identity
            attachment_id (str): blobs/aaaaaaaaaaaaa

        Returns:
            REST response

        identity has one of the following 4 forms:

            [https://app.datatrails.ai/archivist/][v2/] - if public
            assets/xxxxxxxxxxxxxxxxxxxxxxxxxx

            [https://app.datatrails.ai/archivist/][v2/] - if public
            assets/xxxxxxxxxxxxxxxxxxxxxxxxxx/events/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
        """

        return self._archivist.get(f"{self._identity(identity, attachment_id)}/info")
