"""
Mock response object
"""

import json

# pylint: disable=missing-docstring


class MockResponse(dict):
    def __init__(
        self, status_code, request=None, headers=None, iter_content=None, **kwargs
    ):
        super().__init__(**kwargs)
        self.status_code = status_code
        self._headers = headers
        self._request = request
        self._iter_content = iter_content

    @property
    def url(self):
        return "url"

    @property
    def request(self):
        return self._request

    @property
    def headers(self):
        return self._headers

    @property
    def text(self):
        return json.dumps(self)

    def json(self):
        return self

    def iter_content(self, chunk_size=4096):
        return self._iter_content(chunk_size=chunk_size)
