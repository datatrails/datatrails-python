"""Some convenience stuff
"""


from logging import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from io import BytesIO

from requests import get as requests_get

LOGGER = getLogger(__name__)


# pylint: disable=missing-function-docstring
def __tuple_member(tup, idx, default):
    try:
        ret = tup[idx]
    except IndexError:
        ret = default

    return ret


# for confirmers
def backoff_handler(details):
    wait = details["wait"]
    tries = details["tries"]
    args = details["args"]
    client = __tuple_member(args, 0, "")
    identity = __tuple_member(args, 1, "")
    LOGGER.debug(
        "Backing off %0.1f seconds after %s tries with %s id %s",
        wait,
        tries,
        client,
        identity,
    )


# download arbitrary files from a url.
def get_url(url: str, fd: "BytesIO"):  # pragma: no cover
    """GET method (REST) - chunked

    Downloads a binary object from upstream storage.
    """
    response = requests_get(
        url,
        stream=True,
        timeout=30,
    )

    for chunk in response.iter_content(chunk_size=4096):
        if chunk:
            fd.write(chunk)


def get_auth(
    *,
    auth_token_filename=None,
    auth_token=None,
    client_id=None,
    client_secret_filename=None,
    client_secret=None,
):  # pragma: no cover
    """
    Return auth as either stuntidp token or client_id,client_secret tuple
    """

    if auth_token:
        return auth_token

    if auth_token_filename:
        with open(auth_token_filename, mode="r", encoding="utf-8") as tokenfile:
            auth_token = tokenfile.read().strip()

        return auth_token

    if client_id is not None:
        if client_secret_filename is not None:
            with open(client_secret_filename, mode="r", encoding="utf-8") as tokenfile:
                client_secret = tokenfile.read().strip()
            return (client_id, client_secret)

        if client_secret is not None:
            return (client_id, client_secret)

    return None


def selector_signature(selector: list, data: dict) -> "tuple[dict, dict | None]":
    """
    Convert a selector to a signature for list and count methods

    Used in locations.create_if_not_exists and assets.create_if_not_exists
    """
    attrselector = []
    propselector = []

    for k in selector:
        try:
            attrselector = k["attributes"]
        except (KeyError, TypeError):
            propselector.append(k)

    props = {k: data[k] for k in propselector}
    if attrselector:
        data_attrs = data["attributes"]  # keyerror if not exist (it must exist)
        attrs = {k: data_attrs[k] for k in attrselector}
    else:
        attrs = None

    return (props, attrs)
