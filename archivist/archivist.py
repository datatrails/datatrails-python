# -*- coding: utf-8 -*-
"""Archivist connection interface

   This module contains the base Archivist class which manages
   the connection parameters to a DATATRAILS instance and
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
          "https://app.datatrails.ai",
          authtoken,
          max_time=300.0,
      )

    The arch variable now has additional endpoints assets,events,locations,
    attachments, IAM subjects and IAM access policies documented elsewhere.

"""
from copy import deepcopy
from logging import getLogger
from time import time
from typing import Any, BinaryIO

from requests_toolbelt.multipart.encoder import MultipartEncoder

from .access_policies import _AccessPoliciesClient
from .appidp import _AppIDPClient
from .applications import _ApplicationsClient
from .archivistpublic import ArchivistPublic
from .assetattachments import _AssetAttachmentsClient
from .assets import _AssetsRestricted
from .attachments import _AttachmentsClient
from .compliance import _ComplianceClient
from .compliance_policies import _CompliancePoliciesClient
from .composite import _CompositeClient
from .confirmer import MAX_TIME
from .constants import (
    ROOT,
    SEP,
)
from .dictmerge import _dotdict
from .errors import (
    ArchivistError,
    _parse_response,
)
from .events import _EventsRestricted
from .locations import _LocationsClient
from .retry429 import retry_429
from .runner import _Runner
from .subjects import _SubjectsClient
from .tenancies import _TenanciesClient

LOGGER = getLogger(__name__)


class Archivist(ArchivistPublic):  # pylint: disable=too-many-instance-attributes
    """Base class for all Archivist endpoints.

    This class manages the connection to an Archivist instance and provides
    basic methods that represent the underlying REST interface.

    Args:
        url (str): URL of archivist endpoint
        auth: string representing JWT token, or a Tuple pair representing an
        Appregistration ID and secret.
        verify: if True the certificate is verified
        max_time (float): maximum time in seconds to wait for confirmation

    """

    # also change the type hints in __init__ below
    CLIENTS = {
        "access_policies": _AccessPoliciesClient,
        "assets": _AssetsRestricted,
        "assetattachments": _AssetAttachmentsClient,
        "appidp": _AppIDPClient,
        "applications": _ApplicationsClient,
        "attachments": _AttachmentsClient,
        "compliance": _ComplianceClient,
        "compliance_policies": _CompliancePoliciesClient,
        "composite": _CompositeClient,
        "events": _EventsRestricted,
        "locations": _LocationsClient,
        "runner": _Runner,
        "subjects": _SubjectsClient,
        "tenancies": _TenanciesClient,
    }

    def __init__(
        self,
        url: str,
        auth: "str|tuple[str,str]|None",
        *,
        fixtures: "dict[str,dict[Any,Any]]|None" = None,
        verify: bool = True,
        max_time: float = MAX_TIME,
    ):
        super().__init__(
            fixtures=fixtures,
            verify=verify,
            max_time=max_time,
        )

        if isinstance(auth, tuple):
            self._machine_auth = auth
            self._auth = None
        else:
            self._auth = auth
            self._machine_auth = None

        self._expires_at = 0
        if url.endswith("/"):
            raise ArchivistError(f"URL {url} has trailing /")

        self._url = url
        self._root = SEP.join((url, ROOT))

        # Type hints for IDE autocomplete, keep in sync with CLIENTS map above
        self.access_policies: _AccessPoliciesClient
        self.appidp: _AppIDPClient
        self.applications: _ApplicationsClient
        self.assets: _AssetsRestricted
        self.assetattachments: _AssetAttachmentsClient
        self.attachments: _AttachmentsClient
        self.compliance: _ComplianceClient
        self.compliance_policies: _CompliancePoliciesClient
        self.composite: _CompositeClient
        self.events: _EventsRestricted
        self.locations: _LocationsClient
        self.runner: _Runner
        self.subjects: _SubjectsClient
        self.tenancies: _TenanciesClient

    def __str__(self) -> str:
        return f"Archivist({self._url})"

    def __getattr__(self, value: str) -> object:
        """Create endpoints on demand

        This only gets called when an atribute is not found.
        In this case the client attribute in question may not exist.
        """
        LOGGER.debug("getattr %s", value)
        client = self.CLIENTS.get(value)

        if client is None:
            raise AttributeError

        # set attribute so the method is no longer called for this
        # particular client
        c = client(self)
        super().__setattr__(value, c)
        return c

    @property
    def public(self) -> bool:
        """Not a public interface"""
        return False

    @property
    def url(self) -> str:
        """str: URL of Archivist endpoint"""
        return self._url

    @property
    def root(self) -> str:
        """str: ROOT of Archivist endpoint"""
        return self._root

    @property
    def auth(self) -> "str | None":
        """str: authorization token"""

        if self._auth is None and self._machine_auth is None:
            return None

        if self._machine_auth and self._expires_at < time():
            apptoken = self.appidp.token(*self._machine_auth)
            self._auth = apptoken.get("access_token")
            if self._auth is None:
                raise ArchivistError("Auth token from client id,secret is invalid")
            self._expires_at = time() + apptoken["expires_in"] - 10  # fudge factor
            LOGGER.info("Refresh token")

        return self._auth

    @property
    def Public(self) -> ArchivistPublic:  # pylint: disable=invalid-name
        """Get a Public instance"""
        return ArchivistPublic(
            fixtures=deepcopy(self._fixtures),
            verify=self._verify,
            max_time=self._max_time,
        )

    def __copy__(self) -> "Archivist":
        return Archivist(
            self._url,
            self.auth,
            fixtures=deepcopy(self._fixtures),
            verify=self._verify,
            max_time=self._max_time,
        )

    def _add_headers(self, headers: "dict[str,str]|None") -> "dict[str,Any]":
        newheaders = {**headers} if isinstance(headers, dict) else {}

        auth = self.auth  # this may trigger a refetch so only do it once here
        # for appidp endpoint there may not be an authtoken
        if auth is not None:
            newheaders["authorization"] = "Bearer " + auth.strip()

        return newheaders

    # currently only the archivist endpoint is allowed to create/modify data.
    # this may change...
    @retry_429
    def post(
        self,
        url: str,
        request: "dict[str,Any]|None",
        *,
        headers: "dict[str,Any]|None" = None,
        data: "dict[str, Any] | bool" = False,
    ) -> "dict[str, Any]":
        """POST method (REST)

        Creates an entity

        Args:
            url (str): e.g. v2/assets
            request (dict): request body defining the entity
            headers (dict): optional REST headers
            data (bool): send as form-encoded and not as json

        Returns:
            dict representing the response body (entity).
        """
        if data:
            response = self.session.post(
                url,
                data=request,
                verify=self.verify,
            )
        else:
            response = self.session.post(
                url,
                json=request,
                headers=self._add_headers(headers),
                verify=self.verify,
            )

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()

    @retry_429
    def post_file(
        self,
        url: str,
        fd: BinaryIO,
        mtype: "str|None",
        *,
        form: str = "file",
        params: "dict[str, Any]|None" = None,
    ) -> "dict[str, Any]":
        """POST method (REST) - upload binary

        Uploads a file to an endpoint

        Args:
            url (str): e.g. v2/assets
            fd : iterable representing the contents of a file.
            mtype (str): mime type e.g. image/jpg
            params (dict): dictionary of optional path params

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

        response = self.session.post(
            url,
            data=multipart,  # pyright: ignore    https://github.com/requests/toolbelt/issues/312
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
    def delete(
        self, url: str, *, headers: "dict[str, Any]|None" = None
    ) -> "dict[str, Any]":
        """DELETE method (REST)

        Deletes an entity

        Args:
            url (str): e.g. v2/assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            headers (dict): optional REST headers

        Returns:
            dict representing the response body (entity).
        """
        response = self.session.delete(
            url,
            headers=self._add_headers(headers),
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
        url: str,
        request: "dict[str, Any]",
        *,
        headers: "dict[str, Any]| None" = None,
    ) -> "dict[str, Any]":
        """PATCH method (REST)

        Updates the specified entity.

        Args:
            url (str): e.g. v2/assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
            request (dict): request body defining the entity changes.
            headers (dict): optional REST headers

        Returns:
            dict representing the response body (entity).
        """

        response = self.session.patch(
            url,
            json=request,
            headers=self._add_headers(headers),
            verify=self.verify,
        )

        self._response_ring_buffer.appendleft(response)

        error = _parse_response(response)
        if error is not None:
            raise error

        return response.json()
