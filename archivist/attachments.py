"""attachments interface

"""

# pylint:disable=too-few-public-methods

from .constants import ATTACHMENTS_SUBPATH, ATTACHMENTS_LABEL


class _AttachmentsClient:

    def __init__(self, archivist):
        """docstring
        """
        self._archivist = archivist

    def upload(self, fd, *, mtype='image/jpg'):
        """docstring
        """
        return Attachment(**self._archivist.post_file(
            f"{ATTACHMENTS_SUBPATH}/{ATTACHMENTS_LABEL}",
            fd,
            mtype,
        ))

    def download(self, identity, fd):
        """docstring
        """
        return Attachment(**self._archivist.get_file(
            ATTACHMENTS_SUBPATH,
            identity,
            fd,
        ))


class Attachment(dict):
    """Attachment object
    """
