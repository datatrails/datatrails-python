"""Some covenience for confirmers
"""

from logging import getLogger

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
