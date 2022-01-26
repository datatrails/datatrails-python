# -*- coding: utf-8 -*-
"""Archivist connection interface

   This module contains the base Archivist class which manages
   the connection parameters to a Jitsuin Archivist instance and
   the basic REST verbs to GET, POST, PATCH and DELETE entities..

   The REST methods in this class should only be used directly when
   a CRUD endpoint for the specific type of entity is unavailable.
   Current CRUD endpoints are assets, events, locations, attachments.
   IAM subjects and IAM access policies.

   Instantiation of this class encapsulates the URL and authentication
   parameters (the max_time parameter is optional):

   .. code-block:: python

      with open(".auth_token", mode="r", encoding="utf-8") as tokenfile:
          authtoken = tokenfile.read().strip()

      # Initialize connection to Archivist
      arch = Archivist(
          "https://app.rkvst.io",
          authtoken,
          max_time=1200,
      )

    The arch variable now has additional endpoints assets,events,locations,
    attachments, IAM subjects and IAM access policies documented elsewhere.

"""

from logging import getLogger

import json

from collections import deque
from copy import deepcopy
from time import time
from typing import BinaryIO, Dict, List, Optional, Union

import requests
from requests.models import Response
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .constants import (
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ROOT,
    SEP,
    VERBSEP,
)
from .dictmerge import _deepmerge, _dotstring
from .errors import (
    _parse_response,
    ArchivistBadFieldError,
    ArchivistDuplicateError,
    ArchivistHeaderError,
    ArchivistNotFoundError,
)
from .headers import _headers_get
from .retry429 import retry_429

from .confirmer import MAX_TIME

from .access_policies import _AccessPoliciesClient
from .appidp import _AppIDPClient
from .applications import _ApplicationsClient
from .assets import _AssetsClient
from .attachments import _AttachmentsClient
from .compliance import _ComplianceClient
from .compliance_policies import _CompliancePoliciesClient
from .events import _EventsClient
from .locations import _LocationsClient
from .runner import _Runner
from .sboms import _SBOMSClient
from .subjects import _SubjectsClient
from .type_aliases import MachineAuth

LOGGER = getLogger(__name__)

# also change the type hints in __init__ below
CLIENTS = {
    "access_policies": _AccessPoliciesClient,
    "assets": _AssetsClient,
    "appidp": _AppIDPClient,
    "applications": _ApplicationsClient,
    "attachments": _AttachmentsClient,
    "compliance": _ComplianceClient,
    "compliance_policies": _CompliancePoliciesClient,
    "events": _EventsClient,
    "locations": _LocationsClient,
    "runner": _Runner,
    "sboms": _SBOMSClient,
    "subjects": _SubjectsClient,
}


class Archivist:  # pylint: disable=too-many-instance-attributes
    """Base class for all Archivist endpoints.

    This class manages the connection to an Archivist instance and provides
    basic methods that represent the underlying REST interface.

    Args:
        url (str): URL of archivist endpoint
        auth: string representing JWT token.
        verify: if True the certificate is verified
        max_time (int): maximum time in seconds to wait for confirmation

    """

    RING_BUFFER_MAX_LEN = 10

    def __init__(
        self,
        url: str,
        auth: Union[None, str, MachineAuth],
        *,
        fixtures: Optional[Dict] = None,
        verify: bool = True,
        max_time: int = MAX_TIME,
    ):

        self._headers = {"content-type": "application/json"}
        if isinstance(auth, tuple):
            self._auth = None
            self._client_id = auth[0]
            self._client_secret = auth[1]
        else:
            self._auth = auth
            self._client_id = None
            self._client_secret = None

        self._expires_at = 0
        self._url = url
        self._verify = verify
        self._response_ring_buffer = deque(maxlen=self.RING_BUFFER_MAX_LEN)
        self._session = requests.Session()
        self._max_time = max_time
        self._fixtures = fixtures or {}

        # Type hints for IDE autocomplete, keep in sync with CLIENTS map above
        self.access_policies: _AccessPoliciesClient
        self.appidp: _AppIDPClient
        self.applications: _ApplicationsClient
        self.assets: _AssetsClient
        self.attachments: _AttachmentsClient
        self.compliance: _ComplianceClient
        self.compliance_policies: _CompliancePoliciesClient
        self.events: _EventsClient
        self.locations: _LocationsClient
        self.runner: _Runner
        self.sboms: _SBOMSClient
        self.subjects: _SubjectsClient

    def __str__(self) -> str:
        return f"Archivist({self._url})"

    def __getattr__(self, value: str):
        """Create endpoints on demand"""
        client = CLIENTS.get(value)

        if client is None:
            raise AttributeError

        c = client(self)
        super().__setattr__(value, c)
        return c

    @property
    def headers(self) -> Dict:
        """dict: Headers REST headers from response"""
        return self._headers

    @property
    def url(self) -> str:
        """str: URL of Archivist endpoint"""
        return self._url

    @property
    def verify(self) -> bool:
        """bool: Returns True if https connections are to be verified"""
        return self._verify

    @property
    def max_time(self) -> int:
        """bool: Returns maximum time in seconds to wait for confirmation"""
        return self._max_time

    @property
    def auth(self) -> str:
        """str: authorization token."""
        if self._client_id is not None and self._expires_at < time():
            apptoken = self.appidp.token(self._client_id, self._client_secret)  # type: ignore
            self._auth = apptoken["access_token"]
            self._expires_at = time() + apptoken["expires_in"] - 10  # fudge factor
            LOGGER.debug("Refresh token")

        return self._auth  # type: ignore

    @property
    def fixtures(self) -> Dict:
        """dict: Contains predefined attributes for each endpoint"""
        return self._fixtures

    @fixtures.setter
    def fixtures(self, fixtures: Dict):
        """dict: Contains predefined attributes for each endpoint"""
        self._fixtures = _deepmerge(self._fixtures, fixtures)

    def __copy__(self):
        return Archivist(
            self._url,
            self.auth,
            fixtures=deepcopy(self._fixtures),
            verify=self._verify,
            max_time=self._max_time,
        )

    def __add_headers(self, headers: Optional[Dict]) -> Dict:
        if headers is not None:
            newheaders = {**self.headers, **headers}
        else:
            newheaders = self.headers

        auth = self.auth  # this may trigger a refetch so only do it once here
        # for appidp endpoint there may not be an authtoken
        if auth is not None:
            newheaders["authorization"] = "Bearer " + auth.strip()

        return newheaders

    @retry_429
    def get(
        self,
        subpath: str,
        identity: str,
        *,
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        tail: Optional[str] = None,
    ) -> Dict:
        """GET method (REST)

        Args:
            subpath (str): e.g. v2 or iam/v1...
            identity (str): e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            tail (str): endpoint tail e.g. metadata
                        adds extra selector to tail of the endpoint
            headers (dict): optional REST headers
            params (dict): optional query strings

        Returns:
            dict representing the response body (entity).

        """
        response = self._session.get(
            SEP.join([f for f in (self.url, ROOT, subpath, identity, tail) if f]),
            headers=self.__add_headers(headers),
            verify=self.verify,
            params=params,
        )

        self._response_ring_buffer.appendleft(response)

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    @retry_429
    def get_file(
        self,
        subpath: str,
        identity: str,
        fd: BinaryIO,
        *,
        headers: Optional[Dict] = None,
        query: Optional[Dict] = None,
    ) -> Response:
        """GET method (REST) - chunked

        Downloads a binary object from upstream storage.

        Args:
            subpath (str): e.g. v2 or iam/v1
            identity (str): e.g. attachments/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            fd (file): an iterable representing a file (usually from open())
                the file must be opened in binary mode
            headers (dict): optional REST headers
            query (dict): optional query strings

        Returns:
            REST response (not the response body)

        """
        qry = self.__query(query)
        if qry:
            identity = "?".join((identity, qry))

        response = self._session.get(
            SEP.join((self.url, ROOT, subpath, identity)),
            headers=self.__add_headers(headers),
            verify=self.verify,
            stream=True,
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
    def post(
        self,
        path: str,
        request: Optional[Dict],
        *,
        headers: Optional[Dict] = None,
        verb: Optional[str] = None,
        noheaders: bool = False,
    ) -> Dict:
        """POST method (REST)

        Creates an entity

        Args:
            path (str): e.g. v2/assets
            request (dict): request body defining the entity
            headers (dict): optional REST headers
            verb (str): optional REST verb
            noheaders (bool): do not add headers and do not jsnify data

        Returns:
            dict representing the response body (entity).

        """
        url = SEP.join((self.url, ROOT, VERBSEP.join([f for f in (path, verb) if f])))
        LOGGER.debug("POST URL %s", url)
        if noheaders:
            data = request
        else:
            headers = self.__add_headers(headers)
            data = json.dumps(request) if request else None

        response = self._session.post(
            url,
            data=data,
            headers=headers,
            verify=self.verify,
        )

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    @retry_429
    def post_file(
        self,
        path: str,
        fd: BinaryIO,
        mtype: str,
        *,
        form: Optional[str] = "file",
        params: Optional[Dict] = None,
    ) -> Dict:
        """POST method (REST) - upload binary

        Uploads a file to an endpoint

        Args:
            path (str): e.g. v2/assets
            fd : iterable representing the contents of a file.
            mtype (str): mime type e.g. image/jpg
            params (dict): dictiuonary of optional path params

        Returns:
            dict representing the response body (entity).

        """

        multipart = MultipartEncoder(
            fields={
                form: ("filename", fd, mtype),
            }
        )
        headers = {
            "content-type": multipart.content_type,
        }
        if params:
            qry = "&".join(sorted(f"{k}={v}" for k, v in _dotstring(params)))
            path = "?".join((path, qry))

        response = self._session.post(
            SEP.join((self.url, ROOT, path)),
            data=multipart,  # type: ignore    https://github.com/requests/toolbelt/issues/312
            headers=self.__add_headers(headers),
            verify=self.verify,
        )

        self._response_ring_buffer.appendleft(response)

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    @retry_429
    def delete(
        self, subpath: str, identity: str, *, headers: Optional[Dict] = None
    ) -> Dict:
        """DELETE method (REST)

        Deletes an entity

        Args:
            subpath (str): e.g. v2 or iam/v1
            identity (str): e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            headers (dict): optional REST headers

        Returns:
            dict representing the response body (entity).

        """
        response = self._session.delete(
            SEP.join((self.url, ROOT, subpath, identity)),
            headers=self.__add_headers(headers),
            verify=self.verify,
        )

        self._response_ring_buffer.appendleft(response)

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    @retry_429
    def patch(
        self,
        subpath: str,
        identity: str,
        request: Dict,
        *,
        headers: Optional[Dict] = None,
    ) -> Dict:
        """PATCH method (REST)

        Updates the specified entity.

        Args:
            subpath (str): e.g. v2 or iam/v1
            identity (str): e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            request (dict): request body defining the entity changes.
            headers (dict): optional REST headers

        Returns:
            dict representing the response body (entity).

        """

        response = self._session.patch(
            SEP.join((self.url, ROOT, subpath, identity)),
            data=json.dumps(request),
            headers=self.__add_headers(headers),
            verify=self.verify,
        )

        self._response_ring_buffer.appendleft(response)

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    @retry_429
    def __list(self, path, args, *, headers=None) -> Response:
        if args:
            path = "?".join((path, args))

        response = self._session.get(
            SEP.join((self.url, ROOT, path)),
            headers=self.__add_headers(headers),
            verify=self.verify,
        )

        self._response_ring_buffer.appendleft(response)

        error = _parse_response(response)
        if error is not None:
            raise error

        return response

    def last_response(self, *, responses: int = 1) -> List[Response]:
        """Returns the requested number of response objects from the response ring buffer

        Args:
            responses (int): Number of responses to be returned in a list

        Returns:
            list of responses.

        """

        return list(self._response_ring_buffer)[:responses]

    @staticmethod
    def __query(query: Optional[Dict]):
        return query and "&".join(sorted(f"{k}={v}" for k, v in _dotstring(query)))

    def get_by_signature(
        self, path: str, field: str, query: Dict, *, headers: Optional[Dict] = None
    ) -> Dict:
        """GET method (REST) with query string

        Reads an entity indirectly by searching for its signature

        It is expected that the query parameters will result in only a single entity
        being found.

        Args:
            path (str): e.g. v2/assets
            field (str): name of collection of entities e.g assets
            query (dict): selector e.g. {"attributes": {"arc_display_name":"container no. 1"}}
            headers (dict): optional REST headers

        Returns:
            dict representing the entity found.

        Raises:
            ArchivistBadFieldError: field has incorrect value.
            ArchivistNotFoundError: No entity found
            ArchivistDuplicateError: More than one entity matching signature found

        """

        paging = "page_size=2"
        qry = self.__query(query)

        response = self.__list(
            path,
            "&".join((a for a in (paging, qry) if a)),  # type: ignore
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

    def count(self, path: str, *, query: Optional[Dict] = None) -> int:
        """GET method (REST) with query string

        Returns the count of objects that match query

        Args:
            path (str): e.g. v2/assets
            query (dict): selector e.g. {"attributes":{"arc_display_name":"container no. 1"}}

        Returns:
            integer count of entities found.

        Raises:
            ArchivistHeaderError: If the expected count header is not present

        """

        paging = "page_size=1"
        qry = self.__query(query)
        headers = {HEADERS_REQUEST_TOTAL_COUNT: "true"}

        response = self.__list(
            path,
            "&".join((a for a in (paging, qry) if a)),  # type: ignore
            headers=headers,
        )

        count = _headers_get(response.headers, HEADERS_TOTAL_COUNT)  # type: ignore

        if count is None:
            raise ArchivistHeaderError("Did not get a count in the header")

        return int(count)

    def list(
        self,
        path: str,
        field: str,
        *,
        page_size: Optional[int] = None,
        query: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ):
        """GET method (REST) with query string

        Lists entities that match the query dictionary.

        If page size is specified return the list of records in batches of page_size
        until next_page_token in response is null.

        If page size is unspecified return up to the internal limit of records.
        (different for each endpoint)

        Args:
            path (str): e.g. v2/assets
            field (str): name of collection of entities e.g assets
            page_size (int): optional number of items per request e.g. 500
            query (dict): selector e.g. {"confirmation_status": "CONFIRMED", }
            headers (dict): optional REST headers

        Returns:
            iterable that lists entities

        Raises:
            ArchivistBadFieldError: field has incorrect value.

        """

        paging = page_size and f"page_size={page_size}"
        qry = self.__query(query)

        while True:
            response = self.__list(
                path,
                "&".join((a for a in (paging, qry) if a)),  # type: ignore
                headers=headers,
            )
            data = response.json()

            try:
                records = data[field]
            except KeyError as ex:
                raise ArchivistBadFieldError(f"No {field} found") from ex

            for record in records:
                yield record

            token = data.get("next_page_token")
            if not token:
                break

            paging = f"page_token={token}"
