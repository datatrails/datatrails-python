"""Archivist exceptions

   All exceptions are derived from a base ArchivistError class.

"""

import json


class ArchivistError(Exception):
    """Base exception for archivist package"""


class ArchivistBadFieldError(ArchivistError):
    """Incorrect field name in list() method"""


class ArchivistUnconfirmedError(ArchivistError):
    """asset or event failed to confirm after fixed timeout"""


class ArchivistIllegalArgumentError(ArchivistError):
    """Optional keyword arguments are inconsistent"""


class ArchivistBadRequestError(ArchivistError):
    """Ill-formed request or validation error (400)"""


class ArchivistDuplicateError(ArchivistError):
    """Read by signature returns more than one asset"""


class ArchivistUnauthenticatedError(ArchivistError):
    """user is unknown (401)"""


class ArchivistForbiddenError(ArchivistError):
    """User does not have permission (403)"""


class ArchivistNotFoundError(ArchivistError):
    """Entity does not exist (404)"""


class Archivist4xxError(ArchivistError):
    """Any other 4xx error"""


class ArchivistNotImplementedError(ArchivistError):
    """Illegal REST verb (501)"""


class ArchivistUnavailableError(ArchivistError):
    """Service is unavailable (503)"""


class Archivist5xxError(ArchivistError):
    """Any other 5xx error"""


def __identity(response):
    identity = "unknown"
    if response.request:
        req = response.request
        body = getattr(req, "body", None)
        if body:
            # when uploading a file the body attribute is a
            # MultiPartEncoder
            try:
                body = json.loads(body)
            except TypeError:
                pass
            else:
                identity = body.get("identity", "unknown")

    return identity


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
    if status_code < 400:
        return None

    text = response.text or ""

    if 400 <= status_code < 500:
        return {
            400: ArchivistBadRequestError(f"{text} ({status_code})"),
            401: ArchivistUnauthenticatedError(f"{text} ({status_code})"),
            403: ArchivistForbiddenError(f"{text} ({status_code})"),
            404: ArchivistNotFoundError(
                f"{__identity(response)} not found ({status_code})"
            ),
        }.get(status_code, Archivist4xxError(f"{text} ({status_code})"))

    if 500 <= status_code < 600:
        return {
            501: ArchivistNotImplementedError(f"{text} ({status_code})"),
            503: ArchivistUnavailableError(f"{text} ({status_code})"),
        }.get(status_code, Archivist5xxError(f"{text} ({status_code})"))

    return ArchivistError(f"{text} ({status_code})")
