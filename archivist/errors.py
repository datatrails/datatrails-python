"""Archivist exceptions

   All exceptions are derived from a base ArchivistError class.

"""

import json
from logging import getLogger
from typing import Optional

from .constants import HEADERS_RETRY_AFTER
from .headers import _headers_get

LOGGER = getLogger(__name__)


class ArchivistError(Exception):
    """Base exception for archivist package"""


class ArchivistBadFieldError(ArchivistError):
    """Incorrect field name in list() method"""


class ArchivistUnconfirmedError(ArchivistError):
    """asset or event failed to confirm after fixed timeout"""


class ArchivistUnpublishedError(ArchivistError):
    """Sbom failed to publish after fixed timeout"""


class ArchivistUnwithdrawnError(ArchivistError):
    """Sbom failed to be withdrawn after fixed timeout"""


class ArchivistInvalidOperationError(ArchivistError):
    """Runner Operation is invalid"""


class ArchivistBadRequestError(ArchivistError):
    """Ill-formed request or validation error (400)"""


class ArchivistDuplicateError(ArchivistError):
    """Read by signature returns more than one asset"""


class ArchivistUnauthenticatedError(ArchivistError):
    """user is unknown (401)"""


class ArchivistPaymentRequiredError(ArchivistError):
    """A quota has been reached (402)"""


class ArchivistForbiddenError(ArchivistError):
    """User does not have permission (403)"""


class ArchivistNotFoundError(ArchivistError):
    """Entity does not exist (404)"""


class ArchivistTooManyRequestsError(ArchivistError):
    """Too many requests in too short a time (429)"""

    def __init__(self, retry: Optional[str], *args):
        self.retry = float(retry) if retry is not None else 0
        super().__init__(*args)


class Archivist4xxError(ArchivistError):
    """Any other 4xx error"""


class ArchivistNotImplementedError(ArchivistError):
    """Illegal REST verb (501) or option"""


class ArchivistHeaderError(ArchivistError):
    """When the expected header is not received"""


class ArchivistUnavailableError(ArchivistError):
    """Service is unavailable (503)"""


class Archivist5xxError(ArchivistError):
    """Any other 5xx error"""


def __identity(response):
    identity = "unknown"
    if response.request:
        LOGGER.debug("Request %s", response.request)
        req = response.request
        body = getattr(req, "body", None)
        if body:
            # when uploading a file the body attribute is a
            # MultiPartEncoder
            try:
                body = json.loads(body)
            except (TypeError, json.decoder.JSONDecodeError):
                pass
            else:
                identity = body.get("identity", "unknown")

    return identity


def __description(response):
    status_code = response.status_code
    if status_code == 404:
        return f"{__identity(response)} not found ({status_code})"

    text = response.text or ""
    return f"{text} ({status_code})"


def _parse_response(response):
    """Parse REST response

    Validates REST response. This is a convenience function called
    by all REST calls.

    Args:
         response (response): response from underlying REST call

    Returns:
         suitable exception if validation fails, None otherwise

    """

    status_code = response.status_code
    LOGGER.debug("Status %s", status_code)
    if status_code < 400:
        return None

    desc = __description(response)

    if status_code == 429:
        return ArchivistTooManyRequestsError(
            _headers_get(response.headers, HEADERS_RETRY_AFTER),
            desc,
        )

    if 400 <= status_code < 500:
        err, arg = {
            400: (ArchivistBadRequestError, desc),
            401: (ArchivistUnauthenticatedError, desc),
            402: (ArchivistPaymentRequiredError, desc),
            403: (ArchivistForbiddenError, desc),
            404: (ArchivistNotFoundError, desc),
        }.get(status_code, (Archivist4xxError, desc))
        return err(arg)

    if 500 <= status_code < 600:
        err, arg = {
            501: (ArchivistNotImplementedError, desc),
            503: (ArchivistUnavailableError, desc),
        }.get(status_code, (Archivist5xxError, desc))
        return err(arg)

    return ArchivistError(desc)
