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
   parameters:

   .. code-block:: python

      with open(".auth_token", mode="r") as tokenfile:
          authtoken = tokenfile.read().strip()

      # Initialize connection to Archivist
      arch = Archivist(
          "https://rkvst.poc.jitsuin.io",
          auth=authtoken,
      )

    The arch variable now has additional endpoints assets,events,locations,
    attachments, IAM subjects and IAM access policies documented elsewhere.

"""

import logging

import json
from os.path import isfile as os_path_isfile
from typing import IO, Optional
from requests.models import Response

from flatten_dict import flatten
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .constants import (
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ROOT,
    SEP,
)
from .errors import (
    _parse_response,
    ArchivistBadFieldError,
    ArchivistDuplicateError,
    ArchivistIllegalArgumentError,
    ArchivistNotFoundError,
)

from .assets import _AssetsClient
from .events import _EventsClient
from .locations import _LocationsClient
from .attachments import _AttachmentsClient
from .access_policies import _AccessPoliciesClient
from .subjects import _SubjectsClient

LOGGER = logging.getLogger(__name__)

# also change the type hints in __init__ below
CLIENTS = {
    "assets": _AssetsClient,
    "events": _EventsClient,
    "locations": _LocationsClient,
    "attachments": _AttachmentsClient,
    "access_policies": _AccessPoliciesClient,
    "subjects": _SubjectsClient,
}


class Archivist:  # pylint: disable=too-many-instance-attributes
    """Base class for all Archivist endpoints.

    This class manages the connection to an Archivist instance and provides
    basic methods that represent the underlying REST interface.

    Args:
        url (str): URL of archivist endpoint
        auth: string representing JWT token.
        cert: filepath containing both private key and certificate
        verify: if True the certificate is verified

    Raises:
        ArchivistIllegalArgumentError: if neither 'auth' and 'cert' or if
            both 'auth' or 'cert'
        ArchivistNotFoundError: if 'cert' filepath is not readable.

    """

    def __init__(
        self,
        url: str,
        *,
        auth: Optional[str] = None,
        cert: Optional[str] = None,
        verify: bool = True,
    ):

        self._headers = {"content-type": "application/json"}
        if auth is not None:
            self._headers["authorization"] = "Bearer " + auth.strip()

        self._url = url
        self._verify = verify
        if not cert and not auth:
            raise ArchivistIllegalArgumentError("Either auth or cert must be specified")

        if cert and auth:
            raise ArchivistIllegalArgumentError(
                "Either auth or cert must be specified but not both"
            )

        if cert:
            if not os_path_isfile(cert):
                raise ArchivistNotFoundError(f"Cert file {cert} does not exist")

        self._cert = cert

        # keep these in sync with CLIENTS map above
        self.assets: _AssetsClient
        self.events: _EventsClient
        self.locations: _LocationsClient
        self.attachments: _AttachmentsClient
        self.access_policies: _AccessPoliciesClient
        self.subjects: _SubjectsClient

    def __getattr__(self, value: str):
        """Create endpoints on demand"""
        client = CLIENTS.get(value)

        if client is None:
            raise AttributeError

        c = client(self)
        super().__setattr__(value, c)
        return c

    @property
    def headers(self) -> dict:
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
    def cert(self) -> str:
        """str: filepath containing authorisation certificate."""
        return self._cert

    def __add_headers(self, headers):
        """docstring"""
        if headers is not None:
            newheaders = {**self.headers, **headers}
        else:
            newheaders = self.headers

        return newheaders

    def get(
        self, subpath: str, identity: str, *, headers: Optional[dict] = None
    ) -> dict:
        """GET method (REST)

        Args:
            subpath (str): e.g. v2 or iam/v1...
            identity (str): e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            headers (dict): optional REST headers

        Returns:
            dict representing the response body (entity).

        """
        response = requests.get(
            SEP.join((self.url, ROOT, subpath, identity)),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def get_file(
        self, subpath: str, identity: str, fd: IO, *, headers: Optional[dict] = None
    ) -> Response:
        """GET method (REST) - chunked

        Downloads a binary object from upstream storage.

        Args:
            subpath (str): e.g. v2 or iam/v1
            identity (str): e.g. attachments/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            fd (file): an iterable representing a file (usually from open())
                the file must be opened in binary mode
            headers (dict): optional REST headers

        Returns:
            REST response (not the response body)

        """
        response = requests.get(
            SEP.join((self.url, ROOT, subpath, identity)),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
            stream=True,
        )
        error = _parse_response(response)
        if error is not None:
            raise error

        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                fd.write(chunk)

        return response

    def post(self, path: str, request: dict, *, headers: Optional[dict] = None) -> dict:
        """POST method (REST)

        Creates an entity

        Args:
            path (str): e.g. v2/assets
            request (dict): request body defining the entity
            headers (dict): optional REST headers

        Returns:
            dict representing the response body (entity).

        """

        response = requests.post(
            SEP.join((self.url, ROOT, path)),
            data=json.dumps(request),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def post_file(self, path: str, fd: IO, mtype: str) -> dict:
        """POST method (REST) - upload binary

        Uploads a file to an endpoint

        Args:
            path (str): e.g. v2/assets
            fd : iterable representing the contents of a file.
            mtype (str): me-ime type e.g. image/jpeg

        Returns:
            dict representing the response body (entity).

        """

        multipart = MultipartEncoder(
            fields={
                "file": ("filename", fd, mtype),
            }
        )
        headers = {
            "content-type": multipart.content_type,
        }
        response = requests.post(
            SEP.join((self.url, ROOT, path)),
            data=multipart,
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def delete(
        self, subpath: str, identity: str, *, headers: Optional[dict] = None
    ) -> dict:
        """DELETE method (REST)

        Deletes an entity

        Args:
            subpath (str): e.g. v2 or iam/v1
            identity (str): e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            headers (dict): optional REST headers

        Returns:
            dict representing the response body (entity).

        """
        response = requests.delete(
            SEP.join((self.url, ROOT, subpath, identity)),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def patch(
        self,
        subpath: str,
        identity: str,
        request: dict,
        *,
        headers: Optional[dict] = None,
    ) -> dict:
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

        response = requests.patch(
            SEP.join((self.url, ROOT, subpath, identity)),
            data=json.dumps(request),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def __list(self, path, args, *, headers=None):
        if args:
            path = "?".join((path, args))

        response = requests.get(
            SEP.join((self.url, ROOT, path)),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )
        error = _parse_response(response)
        if error is not None:
            raise error

        return response

    @staticmethod
    def __query(query):
        return query and "&".join(
            sorted(f"{k}={v}" for k, v in flatten(query, reducer="dot").items())
        )

    def get_by_signature(
        self, path: str, field: str, query: dict, *, headers: Optional[dict] = None
    ) -> dict:
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
            "&".join((a for a in (paging, qry) if a)),
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

    def count(self, path: str, *, query: Optional[dict] = None) -> int:
        """GET method (REST) with query string

        Returns the count of objects that match query

        Args:
            path (str): e.g. v2/assets
            query (dict): selector e.g. {"attributes":{"arc_display_name":"container no. 1"}}

        Returns:
            integer count of entities found.

        """

        paging = "page_size=1"
        qry = self.__query(query)
        headers = {HEADERS_REQUEST_TOTAL_COUNT: "true"}

        response = self.__list(
            path,
            "&".join((a for a in (paging, qry) if a)),
            headers=headers,
        )

        return int(response.headers[HEADERS_TOTAL_COUNT])

    def list(
        self,
        path: str,
        field: str,
        *,
        page_size: Optional[int] = None,
        query: Optional[dict] = None,
        headers: Optional[dict] = None,
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
                "&".join((a for a in (paging, qry) if a)),
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
