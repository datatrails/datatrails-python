"""Attachments interface

   Direct access to the attachments endpoint

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
      with open("something.jpg") as fd:
          attachment = arch.attachments.upload(fd)

"""

# pylint:disable=too-few-public-methods

import logging

from .constants import ATTACHMENTS_SUBPATH, ATTACHMENTS_LABEL

LOGGER = logging.getLogger(__name__)


class _AttachmentsClient:
    """AttachmentsClient

    Access to attachments entitiies using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist):
        self._archivist = archivist

    def upload(self, fd, *, mtype="image/jpg"):
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

    def download(self, identity, fd):
        """Read attachment

        Reads attachment into data sink (usually a file opened for write)..
        Note that returns the response as the body will be consumed by the
        fd iterator

        Args:
            identity (str): attachment identity e.g. attachments/xxxxxxxxxxxxxxxxxxxxxxx
            fd (file): opened file escriptor or other file-type sink..

        Returns:
            REST response

        """
        return self._archivist.get_file(
            ATTACHMENTS_SUBPATH,
            identity,
            fd,
        )


class Attachment(dict):
    """Attachment

    Attachment object has dictionary attributes.

    """
