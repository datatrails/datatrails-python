"""Some convenience for confirmers
"""

from io import BytesIO
from logging import getLogger
from requests import get as requests_get

LOGGER = getLogger(__name__)


# pylint: disable=missing-function-docstring
def __tuple_member(tup, idx, default):
    try:
        ret = tup[idx]
    except IndexError:
        ret = default

    return ret


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


def get_url(url: str, fd: BytesIO):  # pragma no cover
    """GET method (REST) - chunked

    Downloads a binary object from upstream storage.
    """
    response = requests_get(
        url,
        stream=True,
    )

    for chunk in response.iter_content(chunk_size=4096):
        if chunk:
            fd.write(chunk)
