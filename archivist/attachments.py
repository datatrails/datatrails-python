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
          "https://app.rkvst.io",
          authtoken,
      )
      with open("something.jpg") as fd:
          attachment = arch.attachments.upload(fd)

"""

# pylint:disable=too-few-public-methods

from copy import deepcopy
from io import BytesIO
from logging import getLogger
from typing import BinaryIO, Dict, Optional

from requests.models import Response

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper

from .constants import (
    ASSETS_SUBPATH,
    ATTACHMENTS_SUBPATH,
    ATTACHMENTS_LABEL,
    ATTACHMENTS_ASSETS_EVENTS_LABEL,
    SEP,
)
from .dictmerge import _deepmerge
from .utils import get_url
from .type_aliases import NoneOnError

LOGGER = getLogger(__name__)


class Attachment(dict):
    """Attachment

    Attachment object has dictionary attributes.

    """


class _AttachmentsClient:
    """AttachmentsClient

    Access to attachments entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

    def __str__(self) -> str:
        return f"AttachmentsClient({self._archivist.url})"

    def create(self, data: Dict) -> Dict:  # pragma: no cover
        """
        Create an attachment and return struct suitable for use in an asset
        or event creation.

        Args:
            data (dict): dictionary

        A YAML representation of the data argument would be:

            .. code-block:: yaml

                filename: functests/test_resources/doors/assets/gdn_front.jpg
                content_type: image/jpg
                display_name: arc_primary_image

            OR

            .. code-block:: yaml

                url: https://secure.eicar.org/eicar.com.zip"
                content_type: application/zip
                display_name: Test malware

             Either 'filename' or 'url' is required.
             'content_type' is required.

        Returns:

            A dict suitable for adding to an asset or event creation

        A YAML representation of the result would be:

            .. code-block:: yaml

                arc_display_name: Telephone
                arc_attachment_identity: blobs/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                arc_hash_alg: SHA256
                arc_hash_value: xxxxxxxxxxxxxxxxxxxxxxx

        """
        result = None
        filename = data.get("filename")
        if filename is not None:
            with open(filename, "rb") as fd:
                attachment = self.upload(fd, mtype=data.get("content_type"))

        else:
            url = data["url"]
            fd = BytesIO()
            get_url(url, fd)
            attachment = self.upload(fd, mtype=data.get("content_type"))

        result = {
            "arc_attachment_identity": attachment["identity"],
            "arc_hash_alg": attachment["hash"]["alg"],
            "arc_hash_value": attachment["hash"]["value"],
        }

        display_name = data.get("display_name")
        if display_name is not None:
            result["arc_display_name"] = display_name

        return result

    def upload(self, fd: BinaryIO, *, mtype: str = "image/jpg") -> Attachment:
        """Create attachment

        Creates attachment from opened file or other data source.

        Args:
            fd (file): opened file descriptor or other file-type iterable.
            mtype (str): mimetype of data.

        Returns:
            :class:`Attachment` instance

        """

        LOGGER.debug("Upload Attachment")
        return Attachment(
            **self._archivist.post_file(
                f"{ATTACHMENTS_SUBPATH}/{ATTACHMENTS_LABEL}",
                fd,
                mtype,
            )
        )

    def __params(self, params: Optional[Dict]) -> Dict:
        params = deepcopy(params) if params else {}
        # pylint: disable=protected-access
        return _deepmerge(self._archivist.fixtures.get(ATTACHMENTS_LABEL), params)

    def download(
        self,
        identity: str,
        fd: BinaryIO,
        *,
        params: Optional[Dict] = None,
        asset_or_event_id: Optional[str] = None,
    ) -> Response:
        """Read attachment

        Reads attachment into data sink (usually a file opened for write)..
        Note that returns the response as the body will be consumed by the
        fd iterator

        Args:
            identity (str): attachment identity e.g. attachments/xxxxxxxxxxxxxxxxxxxxxxx
            fd (file): opened file descriptor or other file-type sink..
            params (dict): e.g. {"allow_insecure": "true"} OR {"strict": "true" }
            asset_or_event_id (str): optional asset or event identity

        asset_or_event_id has one of the following forms:

            assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            assets/xxxxxxxxxxxxxxxxxxxxxxxxxx/events/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

        Returns:
            REST response

        """
        if asset_or_event_id is not None:
            uuid = identity.split(SEP)[1]
            identity = SEP.join((asset_or_event_id, uuid))
            return self._archivist.get_file(
                SEP.join((ASSETS_SUBPATH, ATTACHMENTS_ASSETS_EVENTS_LABEL)),
                identity,
                fd,
                params=self.__params(params),
            )

        return self._archivist.get_file(
            ATTACHMENTS_SUBPATH,
            identity,
            fd,
            params=self.__params(params),
        )

    def info(
        self,
        identity: str,
        *,
        asset_or_event_id: Optional[str] = None,
    ) -> Response:
        """Read attachment info

        Reads attachment info

        Args:
            identity (str): attachment identity e.g. attachments/xxxxxxxxxxxxxxxxxxxxxxx
            asset_or_event_id (str): optional asset or event identity

        asset_or_event_id has one of the following forms:

            assets/xxxxxxxxxxxxxxxxxxxxxxxxxx
            assets/xxxxxxxxxxxxxxxxxxxxxxxxxx/events/yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

        Returns:
            REST response

        """
        if asset_or_event_id is not None:
            uuid = identity.split(SEP)[1]
            identity = SEP.join((asset_or_event_id, uuid))
            return self._archivist.get(
                SEP.join((ASSETS_SUBPATH, ATTACHMENTS_ASSETS_EVENTS_LABEL)),
                identity,
                tail="info",
            )

        return self._archivist.get(
            ATTACHMENTS_SUBPATH,
            identity,
            tail="info",
        )
