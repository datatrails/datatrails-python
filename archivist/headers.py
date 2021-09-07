"""Archivist SDK

   Manage headers allowing for upper/lower/canonicalize form
"""


def _headers_get(headers: dict, key: str) -> str:
    if headers is not None:
        ret = headers.get(key)
        if ret is not None:
            return ret
        return headers.get(key.lower())

    return None
