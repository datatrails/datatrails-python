"""Archivist connection interface (python 3.8)

   Uses CRUDL - user is expected to know the values of the various constants
   The comment details how this may be used for assets - other endpoints
   will require differing values.

   This class is sufficient for all endpoints but differeneces for each endpoint
   will have to be documented. We can do better.

"""

import json
from os.path import isfile as os_path_isfile

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
    parse_response,
    ArchivistBadFieldError,
    ArchivistDuplicateError,
    ArchivistIllegalArgumentError,
    ArchivistNotFoundError,
)

from .assets import _AssetsClient
from .events import _EventsClient
from .locations import _LocationsClient
from .attachments import _AttachmentsClient


class Archivist:  # pylint: disable=too-many-instance-attributes
    """docstring

    auth: string representing JWT token.
    cert: filepath containing both private key and certificate

    Either auth or cert must be specified
    """
    def __init__(self, url, *, auth=None, cert=None, verify=True):
        """docstring
        """
        self._headers = {'content-type': 'application/json'}
        if auth is not None:
            self._headers['authorization'] = 'Bearer ' + auth.strip()

        self._url = url
        self._verify = verify
        if not cert and not auth:
            raise ArchivistIllegalArgumentError(
                "Either auth or cert must be specified"
            )

        if cert and auth:
            raise ArchivistIllegalArgumentError(
                "Either auth or cert must be specified but not both"
            )

        if cert:
            if not os_path_isfile(cert):
                raise ArchivistNotFoundError(
                    f"Cert file {cert} does not exist"
                )

        self._cert = cert

        self.assets = _AssetsClient(self)
        self.events = _EventsClient(self)
        self.locations = _LocationsClient(self)
        self.attachments = _AttachmentsClient(self)

    @property
    def headers(self):
        """docstring
        """
        return self._headers

    @property
    def url(self):
        """docstring
        """
        return self._url

    @property
    def verify(self):
        """docstring
        """
        return self._verify

    @property
    def cert(self):
        """docstring
        """
        return self._cert

    def __add_headers(self, headers):
        """docstring
        """
        if headers is not None:
            newheaders = {**self.headers, **headers}
        else:
            newheaders = self.headers

        return newheaders

    def get(self, subpath, identity, *, headers=None):
        """
        subpath: e.g. v2 or iam/v1
        identity: e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
        """
        response = requests.get(
            SEP.join((self.url, ROOT, subpath, identity)),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def get_file(self, subpath, identity, fd, *, headers=None):
        """
        subpath: e.g. v2 or iam/v1
        identity: e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
        fd: an iterable representing a file (usually from open())
        """
        response = requests.get(
            SEP.join((self.url, ROOT, subpath, identity)),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
            stream=True,
        )
        error = parse_response(response)
        if error is not None:
            raise error

        for chunk in response.iter_content(chunk_size=4096):
            if chunk:
                fd.write(chunk)

        return response.json()

    def post(self, path, request, *, headers=None):
        """
        path: e.g. v2/assets
        """

        response = requests.post(
            SEP.join((self.url, ROOT, path)),
            data=json.dumps(request),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def post_file(self, path, fd, mtype):
        """

        Uploads a file to an endpoint

        path: e.g. v1/blobs
        fd: an iterable representing a file (usually from open())
        mtype: mime tiype (image/jpg)
        """

        multipart = MultipartEncoder(
            fields={
                'file': ('filename', fd, mtype),
            }
        )
        headers = {
            'content-type': multipart.content_type,
        }
        response = requests.post(
            SEP.join((self.url, ROOT, path)),
            data=multipart,
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def delete(self, subpath, identity, *, headers=None):
        """
        subpath: e.g. v2 or iam/v1
        identity: e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
        """
        response = requests.delete(
            SEP.join((self.url, ROOT, subpath, identity)),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def patch(self, subpath, identity, request, *, headers=None):
        """
        subpath: e.g. v2 or iam/v1
        identity: e.g. assets/xxxxxxxxxxxxxxxxxxxxxxxxxxxx`
        """

        response = requests.patch(
            SEP.join((self.url, ROOT, subpath, identity)),
            data=json.dumps(request),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )

        error = parse_response(response)
        if error is not None:
            raise error

        return response.json()

    def __list(self, path, args, *, headers=None):
        if args:
            path = '?'.join((path, args))

        response = requests.get(
            SEP.join((self.url, ROOT, path)),
            headers=self.__add_headers(headers),
            verify=self.verify,
            cert=self.cert,
        )
        error = parse_response(response)
        if error is not None:
            raise error

        return response

    @staticmethod
    def __query(query):
        return query and '&'.join(
            sorted(
                f"{k}={v}" for k, v in flatten(query, reducer='dot').items()
            )
        )

    def get_by_signature(self, path, field, *, query=None, headers=None):
        """Reads an entity indirectly by suearching for its signature

        It is expected that the query parameters will result in only a single entity
        being returned.

        path: e.g. v2/assets
        query: query dictionary e.g. {"confirmation_status": "CONFIRMED", }
        """

        paging = "page_size=2"
        qry = self.__query(query)

        response = self.__list(
            path,
            '&'.join(
                (a for a in (paging, qry) if a)
            ),
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

    def count(self, path, *, query=None):
        """Returns the count of objects that meet query

        path: e.g. v2/assets
        query: query dictionary e.g. {"confirmation_status": "CONFIRMED", }
        """

        paging = "page_size=1"
        qry = self.__query(query)
        headers = {HEADERS_REQUEST_TOTAL_COUNT: 'true'}

        # v2/assets?page_size=10&something=something...

        response = self.__list(
            path,
            '&'.join(
                (a for a in (paging, qry) if a)
            ),
            headers=headers,
        )

        return int(response.headers[HEADERS_TOTAL_COUNT])

    def list(self, path, field, *, page_size=None, query=None, headers=None):
        """Returns generator that lists objects

        path: e.g. v2/assets
        field: e.g. assets - collective noun of entity
        page_size: optional number of items per request e.g. 50
        query: query dictionary e.g. {"confirmation_status": "CONFIRMED", }

        If page size is specified return the list of records in batches of page_size
        until next_page_token in response is null.

        If page size is unspecified return up to the internal limit of records.
        (different for each endpoint)
        """

        paging = page_size and f"page_size={page_size}"
        qry = self.__query(query)

        # v2/assets?page_size=10&something=something...

        while True:
            response = self.__list(
                path,
                '&'.join(
                    (a for a in (paging, qry) if a)
                ),
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
