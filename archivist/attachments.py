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

from typing import BinaryIO, Dict, Optional
from copy import deepcopy
from logging import getLogger

from requests.models import Response

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper

from .constants import ATTACHMENTS_SUBPATH, ATTACHMENTS_LABEL
from .dictmerge import _deepmerge
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

    def __query(self, params: Optional[Dict]) -> Dict:
        query = deepcopy(params) if params else {}
        # pylint: disable=protected-access
        return _deepmerge(self._archivist.fixtures.get(ATTACHMENTS_LABEL), query)

    def download(
        self,
        identity: str,
        fd: BinaryIO,
        *,
        query: Optional[Dict] = None,
    ) -> Response:
        """Read attachment

        Reads attachment into data sink (usually a file opened for write)..
        Note that returns the response as the body will be consumed by the
        fd iterator

        Args:
            identity (str): attachment identity e.g. attachments/xxxxxxxxxxxxxxxxxxxxxxx
            fd (file): opened file escriptor or other file-type sink..
            query (dict): e.g. {"allow_insecure": "true"} OR {"strict": "true" }

        Returns:
            REST response

        """
        return self._archivist.get_file(
            ATTACHMENTS_SUBPATH,
            identity,
            fd,
            query=self.__query(query),
        )
