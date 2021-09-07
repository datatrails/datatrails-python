"""retry when 429 is received

   Retries after waiting for the time read from the retry-after header
"""

from functools import wraps
import logging
from time import sleep

from .errors import ArchivistTooManyRequestsError

NO_OF_RETRIES = 3
LOGGER = logging.getLogger(__name__)


def retry_429(f):
    """
    Retry when 429 received using sleep suggested by retry_after header
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        no_of_retries = NO_OF_RETRIES
        while True:
            try:
                ret = f(*args, **kwargs)
            except ArchivistTooManyRequestsError as ex:
                if ex.retry <= 0 or no_of_retries <= 0:
                    raise
                sleep(ex.retry)
                no_of_retries -= 1

            else:
                return ret

    return wrapper
