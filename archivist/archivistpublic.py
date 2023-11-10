# -*- coding: utf-8 -*-
"""Public connection interface

   This module contains the base Archivist class which manages
   the public connection to an DataTrails instance and
   the basic REST verbs to GET, POST, PATCH and DELETE entities..

   The REST methods in this class should only be used directly when
   a CRUD endpoint for the specific type of entity is unavailable.
   Current CRUD endpoints are assets, events.
   Instantiation of this class encapsulates the URL and authentication
   parameters (the max_time parameter is optional):

   .. code-block:: python

      # Initialize connection to Archivist
      public = :Public(
          max_time=300.0,
      )

    The public variable now has additional endpoints assets,events.

"""

from collections import deque
from copy import deepcopy
from logging import getLogger
from typing import TYPE_CHECKING, Any, BinaryIO

import requests

if TYPE_CHECKING:
    from requests.models import Response


from .assetattachments import _AssetAttachmentsClient
from .assets import _AssetsPublic
from .confirmer import MAX_TIME
from .constants import (
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
)
from .dictmerge import _deepmerge, _dotdict
from .errors import (
    ArchivistBadFieldError,
    ArchivistDuplicateError,
    ArchivistHeaderError,
    ArchivistNotFoundError,
    _parse_response,
)
from .events import _EventsPublic
from .headers import _headers_get
from .retry429 import retry_429

LOGGER = getLogger(__name__)


class ArchivistPublic:  # pylint: disable=too-many-instance-attributes
    """Base class for public Archivist endpoints.

    This class manages the connection to an Archivist instance and provides
    basic methods that represent the underlying REST interface.

    Args:
        verify: if True the certificate is verified
        max_time (float): maximum time in seconds to wait for confirmation

    """

    # also change the type hints in __init__ below
    CLIENTS = {
        "assets": _AssetsPublic,
        "events": _EventsPublic,
        "assetattachments": _AssetAttachmentsClient,
    }

    RING_BUFFER_MAX_LEN = 10

    def __init__(
        self,
        *,
        fixtures: "dict[str, Any]|None" = None,
        verify: bool = True,
        max_time: float = MAX_TIME,
    ):
        self._verify = verify
        self._response_ring_buffer = deque(maxlen=self.RING_BUFFER_MAX_LEN)
        self._session = None
        self._max_time = max_time
        self._fixtures = fixtures or {}

        # Type hints for IDE autocomplete, keep in sync with CLIENTS map above
        self.assets: _AssetsPublic
        self.events: _EventsPublic
        self.assetattachments: _AssetAttachmentsClient

    def __str__(self) -> str:
        return "ArchivistPublic()"

    def __getattr__(self, value: str) -> object:
        """Create endpoints on demand"""
        client = self.CLIENTS.get(value)

        if client is None:
            raise AttributeError

        c = client(self)
        super().__setattr__(value, c)
        return c

    def __enter__(self):
        """Just return self on entering - the session property will
        create the session when needed
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def session(self) -> requests.Session:
        """creates and returns session"""
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def close(self):
        """closes current session if open"""
        if self._session is not None:
            self._session.close()
            self._session = None

    @property
    def public(self) -> bool:
        """This is a public interface"""
        return True

    @property
    def root(self) -> str:
        """str: ROOT of Public endpoint"""
        return ""

    @property
    def verify(self) -> bool:
        """bool: Returns True if https connections are to be verified"""
        return self._verify

    @property
    def max_time(self) -> float:
        """bool: Returns maximum time in seconds to wait for confirmation"""
        return self._max_time

    @property
    def fixtures(self) -> "dict[str, Any]":
        """dict: Contains predefined attributes for each endpoint"""
        return self._fixtures

    @fixtures.setter
    def fixtures(self, fixtures: "dict[str, Any]"):
        """dict: Contains predefined attributes for each endpoint"""
        self._fixtures = _deepmerge(self._fixtures, fixtures)

    def __copy__(self):
        return ArchivistPublic(
            fixtures=deepcopy(self._fixtures),
            verify=self._verify,
            max_time=self._max_time,
        )

    def _add_headers(self, headers: "dict[str, str]|None") -> "dict[str, str]":
        newheaders = {**headers} if headers is not None else {}

        return newheaders

    # the public endpoint is currently readonly so only read-type methods are
    # defined here. This may change - the Public endpoint may allow writes
    # in future...
    @retry_429
    def get(
        self,
        url: str,
        *,
        headers: "dict[str, str]|None" = None,
        params: "dict[str, Any]|None" = None,
    ) -> "dict[str, Any]":
        """GET method (REST)

        Args:
            url (str): e.g. https://app.datatrails.ai/archivist/v2/publicassets/xxxxxxxxxxxxxxxxxx
            headers (dict): optional REST headers
            params (dict): optional params strings

        Returns:
            dict representing the response body (entity).

        """
        response = self.session.get(
            url,
            headers=self._add_headers(headers),
            verify=self.verify,
            params=_dotdict(params),
        )

        self._response_ring_buffer.appendleft(response)

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    @retry_429
    def get_file(
        self,
        url: str,
        fd: BinaryIO,
        *,
        headers: "dict[str, str]|None" = None,
        params: "dict[str, Any]|None" = None,
    ) -> "Response":
        """GET method (REST) - chunked

        Downloads a binary object from upstream storage.

        Args:
            url (str): e.g. assets/xxxxxxxxxxxxxxxxxxxxxx
            identity (str): e.g. blobs/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            fd (file): an iterable representing a file (usually from open())
                the file must be opened in binary mode
            headers (dict): optional REST headers
            params (dict): optional params strings

        Returns:
            REST response (not the response body)

        """
        response = self.session.get(
            url,
            headers=self._add_headers(headers),
            verify=self.verify,
            stream=True,
            params=_dotdict(params),
        )

        self._response_ring_buffer.appendleft(response)

        error = _parse_response(response)
        if error is not None:
            raise error

        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                fd.write(chunk)

        return response

    @retry_429
    def __list(
        self,
        url: str,
        params: "dict[str, Any]|None",
        *,
        page_size: "int|None" = None,
        headers: "dict[str, str]|None" = None,
    ) -> "Response":
        if page_size is not None:
            if params is not None:
                params["page_size"] = page_size
            else:
                params = {"page_size": page_size}

        response = self.session.get(
            url,
            headers=self._add_headers(headers),
            verify=self.verify,
            params=_dotdict(params),
        )

        self._response_ring_buffer.appendleft(response)

        error = _parse_response(response)
        if error is not None:
            raise error

        return response

    def last_response(self, *, responses: int = 1) -> "list[Response]":
        """Returns the requested number of response objects from the response ring buffer

        Args:
            responses (int): Number of responses to be returned in a list

        Returns:
            list of responses.

        """

        return list(self._response_ring_buffer)[:responses]

    def get_by_signature(
        self,
        url: str,
        field: str,
        params: "dict[str, Any]",
        *,
        headers: "dict[str, str]|None" = None,
    ) -> "dict[str, Any]":
        """GET method (REST) with params string

        Reads an entity indirectly by searching for its signature

        It is expected that the params parameters will result in only a single entity
        being found.

        Args:
            url (str): e.g. https://app.datatrails.ai/archivist/v2/assets
            field (str): name of collection of entities e.g assets
            params (dict): selector e.g. {"attributes": {"arc_display_name":"container no. 1"}}
            headers (dict): optional REST headers

        Returns:
            dict representing the entity found.

        Raises:
            ArchivistBadFieldError: field has incorrect value.
            ArchivistNotFoundError: No entity found
            ArchivistDuplicateError: More than one entity matching signature found

        """

        response = self.__list(
            url,
            params,
            page_size=2,
            headers=headers,
        )

        data = response.json()

        try:
            records = data[field]
        except KeyError as ex:
            raise ArchivistBadFieldError(f"No {field} found") from ex

        if len(records) == 0:
            raise ArchivistNotFoundError("No entity found")

        if len(records) > 1:
            raise ArchivistDuplicateError(f"{len(records)} found")

        return records[0]

    def count(self, url: str, *, params: "dict[str, Any]|None" = None) -> int:
        """GET method (REST) with params string

        Returns the count of objects that match params

        Args:
            url (str): e.g. https://app.datatrails.ai/archivist/v2/assets
            params (dict): selector e.g. {"attributes":{"arc_display_name":"container no. 1"}}

        Returns:
            integer count of entities found.

        Raises:
            ArchivistHeaderError: If the expected count header is not present

        """

        response = self.__list(
            url,
            params,
            page_size=1,
            headers={HEADERS_REQUEST_TOTAL_COUNT: "true"},
        )

        count = _headers_get(response.headers, HEADERS_TOTAL_COUNT)

        if count is None:
            raise ArchivistHeaderError("Did not get a count in the header")

        return int(count)

    def list(
        self,
        url: str,
        field: str,
        *,
        page_size: "int|None" = None,
        params: "dict[str, Any]|None" = None,
        headers: "dict[str, str]|None" = None,
    ):
        """GET method (REST) with params string

        Lists entities that match the params dictionary.

        If page size is specified return the list of records in batches of page_size
        until next_page_token in response is null.

        If page size is unspecified return up to the internal limit of records.
        (different for each endpoint)

        Args:
            url (str): e.g. https://app.datatrails.ai/archivist/v2/assets
            field (str): name of collection of entities e.g assets
            page_size (int): optional number of items per request e.g. 500
            params (dict): selector e.g. {"confirmation_status": "CONFIRMED", }
            headers (dict): optional REST headers

        Returns:
            iterable that lists entities

        Raises:
            ArchivistBadFieldError: field has incorrect value.

        """

        while True:
            response = self.__list(
                url,
                params,
                page_size=page_size,
                headers=headers,
            )
            data = response.json()

            try:
                records = data[field]
            except KeyError as ex:
                raise ArchivistBadFieldError(f"No {field} found") from ex

            for record in records:
                yield record

            page_token = data.get("next_page_token")
            if not page_token:
                break

            params = {"page_token": page_token}
