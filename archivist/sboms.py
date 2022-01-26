"""SBOMS interface

   Direct access to the sboms endpoint

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
      with open("bom.xml") as fd:
          sbom = arch.sboms.upload(fd)

"""

# pylint:disable=too-few-public-methods

from typing import BinaryIO, Dict, Optional
from copy import deepcopy
from logging import getLogger

from requests.models import Response

# pylint:disable=unused-import      # To prevent cyclical import errors forward referencing is used
# pylint:disable=cyclic-import      # but pylint doesn't understand this feature
from . import archivist as type_helper

from .constants import (
    SBOMS_SUBPATH,
    SBOMS_LABEL,
    SBOMS_METADATA,
    SBOMS_WILDCARD,
    SBOMS_WITHDRAW,
    SBOMS_PUBLISH,
)
from . import publisher, uploader, withdrawer
from .dictmerge import _deepmerge
from .sbommetadata import SBOM

LOGGER = getLogger(__name__)


class _SBOMSClient:
    """SBOMSClient

    Access to SBOMs entities using CRUD interface. This class is usually
    accessed as an attribute of the Archivist class.

    Args:
        archivist (Archivist): :class:`Archivist` instance

    """

    def __init__(self, archivist: "type_helper.Archivist"):
        self._archivist = archivist

    def __str__(self) -> str:
        return f"SBOMSClient({self._archivist.url})"

    def upload(
        self,
        fd: BinaryIO,
        *,
        confirm: bool = False,
        mtype: str = "text/xml",
        params: Optional[Dict] = None,
    ) -> SBOM:
        """Create SBOM

        Creates SBOM from opened file or other data source.

        Args:
            fd (file): opened file descriptor or other file-type iterable.
            confirm (bool): if True wait for sbom to be uploaded.
            mtype (str): mimetype of data.
            params (dict): optional e.g. {"sbomType": "cyclonedx-xml", "privacy": "PUBLIC" }

        Returns:
            :class:`SBOM` instance

        """

        LOGGER.debug("Upload SBOM %s", params)

        sbom = SBOM(
            **self._archivist.post_file(
                f"{SBOMS_SUBPATH}/{SBOMS_LABEL}",
                fd,
                mtype,
                form="sbom",
                params=params,
            )
        )
        if not confirm:
            return sbom

        return self.wait_for_uploading(sbom.identity)

    def wait_for_uploading(self, identity: str) -> SBOM:
        """Wait for sbom to be uploaded.

        Waits for sbom to be uploaded.

        Args:
            identity (str): identity of sbom

        Returns:
            True if sbom is uploaded.

        """
        uploader.MAX_TIME = self._archivist.max_time
        # pylint: disable=protected-access
        return uploader._wait_for_uploading(self, identity)  # type: ignore

    def download(self, identity: str, fd: BinaryIO) -> Response:
        """Read SBOM

        Reads SBOM into data sink (usually a file opened for write)..
        Note that returns the response as the body will be consumed by the
        fd iterator

        Args:
            identity (str): SBOM identity e.g. sboms/xxxxxxxxxxxxxxxxxxxxxxx
            fd (file): opened file descriptor or other file-type sink.

        Returns:
            REST response

        """
        return self._archivist.get_file(
            SBOMS_SUBPATH,
            identity,
            fd,
        )

    def read(self, identity: str) -> SBOM:
        """Read SBOM metadata

        Reads SBOM metadata.

        Args:
            identity (str): sbom identity e.g. sboms/xxxxxxxxxxxxxxxxxxxxxxx

        Returns:
            BOM

        """
        return SBOM(
            **self._archivist.get(
                SBOMS_SUBPATH,
                identity,
                tail=SBOMS_METADATA,
            )
        )

    def __query(self, metadata: Optional[Dict]) -> Dict:
        query = deepcopy(metadata) if metadata else {}
        return _deepmerge(self._archivist.fixtures.get(SBOMS_LABEL), query)

    def list(
        self,
        *,
        page_size: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ):
        """List SBOMS.

        Lists SBOMS that match optional criteria:

        .. code-block:: python

            sboms = self.arch.sboms.list(metadata={
                "trusted": True,
                "uploaded_before": "2021-11-17T11:28:31Z",
                "uploaded_since": "2021-11-16T11:28:31Z",
            })

        Args:
            metadata (dict): optional e.g. {"life_cycle_status": "ACTIVE" }
            page_size (int): optional page size. (Rarely used).

        Returns:
            iterable that returns :class:`SBOM` instances

        """
        query = self.__query(metadata)
        return (
            SBOM(**a)
            for a in self._archivist.list(
                f"{SBOMS_SUBPATH}/{SBOMS_LABEL}/{SBOMS_WILDCARD}",
                SBOMS_LABEL,
                page_size=page_size,
                query=query,
            )
        )

    def publish(self, identity: str, confirm: bool = False) -> SBOM:
        """Publish SBOMt

        Makes an SBOM public.

        Args:
            identity (str): identity of SBOM
            confirm (bool): if True wait for sbom to be published.

        Returns:
            :class:`SBOM` instance

        """
        LOGGER.debug("Publish SBOM %s", identity)
        sbom = SBOM(
            **self._archivist.post(
                f"{SBOMS_SUBPATH}/{identity}",
                None,
                verb=SBOMS_PUBLISH,
            )
        )
        if not confirm:
            return sbom

        return self.wait_for_publication(sbom.identity)

    def wait_for_publication(self, identity: str) -> SBOM:
        """Wait for sbom to be published.

        Waits for sbom to be published.

        Args:
            identity (str): identity of sbom

        Returns:
            True if sbom is confirmed.

        """
        publisher.MAX_TIME = self._archivist.max_time
        # pylint: disable=protected-access
        return publisher._wait_for_publication(self, identity)  # type: ignore

    def withdraw(self, identity: str, confirm: bool = False) -> SBOM:
        """Withdraw SBOM

        Withdraws an SBOM.

        Args:
            identity (str): identity of SBOM
            confirm (bool): if True wait for sbom to be withdrawn.

        Returns:
            :class:`SBOM` instance

        """
        LOGGER.debug("Withdraw SBOM %s", identity)
        sbom = SBOM(
            **self._archivist.post(
                f"{SBOMS_SUBPATH}/{identity}",
                None,
                verb=SBOMS_WITHDRAW,
            )
        )
        if not confirm:
            return sbom

        return self.wait_for_withdrawn(sbom.identity)

    def wait_for_withdrawn(self, identity: str) -> SBOM:
        """Wait for sbom to be withdrawn.

        Waits for sbom to be withdrawn.

        Args:
            identity (str): identity of sbom

        Returns:
            True if sbom is confirmed.

        """
        withdrawer.MAX_TIME = self._archivist.max_time
        # pylint: disable=protected-access
        return withdrawer._wait_for_withdrawn(self, identity)  # type: ignore
