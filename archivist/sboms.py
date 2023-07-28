"""SBOMS interface

   Convenience methods for handling sbom attachments

"""

# pylint:disable=too-few-public-methods


from io import BytesIO
from logging import getLogger
from typing import Any

from xmltodict import parse as xmltodict_parse

from .utils import get_url

LOGGER = getLogger(__name__)


def sboms_parse(data: "dict[str, Any]") -> "dict[str, Any]":  # pragma: no cover
    """
    parse the sbom and extract pertinent information

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
