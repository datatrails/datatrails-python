"""Archivist SDK

   Manage headers allowing for upper/lower/canonicalize form
"""


from requests import models


def _headers_get(headers: models.CaseInsensitiveDict, key: str) -> "str|None":
    if headers is not None:
        ret = headers.get(key)
        if ret is not None:
            return ret
        return headers.get(key.lower())

    return None
