"""Archivist SDK

   Manage headers allowing for upper/lower/canonicalize form
"""


from typing import Dict, Optional


def _headers_get(headers: Dict, key: str) -> Optional[str]:
    if headers is not None:
        ret = headers.get(key)
        if ret is not None:
            return ret
        return headers.get(key.lower())

    return None
