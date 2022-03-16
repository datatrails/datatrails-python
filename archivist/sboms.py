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
from io import BytesIO
from logging import getLogger

from requests.models import Response
from xmltodict import parse as xmltodict_parse

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
from .utils import get_url

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

    @staticmethod
    def parse(data: Dict) -> Dict:  # pragma: no cover
        """
        parse the sbom and extract pertinent informtion

        Args:
            data (dict): dictionary

        A YAML representation of the data argument would be:

            .. code-block:: yaml

                filename: functests/test_resources/sboms/gen1.xml

            OR

            .. code-block:: yaml

                url: https://some.hostname/cdx.xml

             Either 'filename' or 'url' is required.

        Returns:

            A dict suitable for adding to an asset or event creation

        """
        result = None
        filename = data.get("filename")
        if filename is not None:
            with open(filename, "rb") as fd:
                sbom = xmltodict_parse(fd, xml_attribs=True, disable_entities=False)

        else:
            url = data["url"]
            fd = BytesIO()
            get_url(url, fd)
            sbom = xmltodict_parse(fd, xml_attribs=True, disable_entities=False)

        b = sbom["bom"]
        m = b["metadata"]
        c = m["component"]

        result = {
            "author": c["author"],
            "component": c["name"],
            "supplier": c["supplier"]["name"],
            "version": c["version"],
        }

        uuid = b.get("@serialNumber")
        if uuid is not None:
            result["uuid"] = uuid

        try:
            hash_value = c["hashes"]["hash"]["#text"]
        except (TypeError, KeyError):
            pass
        else:
            result["hash"] = hash_value

        return result

    def create(self, data: Dict) -> Dict:  # pragma: no cover
        """
        Create an sbom and return struct suitable for use in an asset
        or event creation.

        Args:
            data (dict): dictionary

        A YAML representation of the data argument would be:

            .. code-block:: yaml

                filename: functests/test_resources/sboms/gen1.xml
                content_type: text/xml
                confirm: True
                params:
                  privacy: PRIVATE

            OR

            .. code-block:: yaml

                url: https://some.hostname/cdx.xml
                content_type: text/xml
                confirm: True
                params:
                  privacy: PRIVATE

             Either 'filename' or 'url' is required.
             'content_type' is required.

        Returns:

            A dict suitable for adding to an asset or event creation

        A YAML representation of the result would be:

            .. code-block:: yaml

                arc_display_name: Acme Generation1 SBOM
                arc_attachment_identity: sboms/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                .....

        """
        result = None
        filename = data.get("filename")
        if filename is not None:
            with open(filename, "rb") as fd:
                sbom = self.upload(
                    fd,
                    confirm=data.get("confirm", False),
                    mtype=data.get("content_type"),
                    params=data.get("params"),
                )

        else:
            url = data["url"]
            fd = BytesIO()
            get_url(url, fd)
            sbom = self.upload(
                fd,
                confirm=data.get("confirm", False),
                mtype=data.get("content_type"),
                params=data.get("params"),
            )

        # response to sbom upload contains all the info we need.
        s = sbom.dict()
        _, hash_value = s["hashes"][0].split(":")
        result = {
            "author": ",".join(s["authors"]),
            "component": s["component"],
            "identity": s["identity"],
            "hash": hash_value,
            "supplier": s["supplier"],
            "uuid": s["unique_id"],
            "version": s["version"],
        }

        return result

    def upload(
        self,
        fd: BinaryIO,
        *,
        confirm: bool = False,
        mtype: Optional[str] = None,
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

        mtype = mtype or "text/xml"

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

    def __params(self, metadata: Optional[Dict]) -> Dict:
        params = deepcopy(metadata) if metadata else {}
        return _deepmerge(self._archivist.fixtures.get(SBOMS_LABEL), params)

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
        params = self.__params(metadata)
        return (
            SBOM(**a)
            for a in self._archivist.list(
                f"{SBOMS_SUBPATH}/{SBOMS_LABEL}/{SBOMS_WILDCARD}",
                SBOMS_LABEL,
                page_size=page_size,
                params=params,
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
