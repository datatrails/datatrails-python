"""
Test SBOMS
"""

from io import BytesIO
import json
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    SBOMS_SUBPATH,
    SBOMS_LABEL,
    SBOMS_METADATA,
    SBOMS_PUBLISH,
    SBOMS_WILDCARD,
    SBOMS_WITHDRAW,
)
from archivist.errors import ArchivistUnpublishedError, ArchivistUnwithdrawnError
from archivist.sbommetadata import SBOM

from .mock_response import MockResponse

# pylint: disable=protected-access
# pylint: disable=unused-variable


PROPS = {
    "identity": "sboms/c3da0d3a-32bf-4f5f-a8c6-b342a8356480",
    "authors": [],
    "supplier": "",
    "component": "keycloak-parent",
    "version": "10.0.2",
    "hashes": [],
    "unique_id": "urn:uuid:411dafd2-c29f-491a-97d7-e97de5bc2289",
    "upload_date": "2021-11-11T17:02:06Z",
    "uploaded_by": "",
    "trusted": False,
    "lifecycle_status": "Active",
    "published_date": "",
    "withdrawn_date": "",
}
PUBLISHED_PROPS = {**PROPS, **{"published_date": "2021-11-11T17:02:06Z"}}
WITHDRAWN_PROPS = {**PROPS, **{"withdrawn_date": "2021-11-11T17:02:06Z"}}

IDENTITY = f"{SBOMS_LABEL}/xxxxxxxx"
SUBPATH = f"{SBOMS_SUBPATH}/{SBOMS_LABEL}"

RESPONSE = {
    **PROPS,
    "identity": IDENTITY,
}
PUBLISHED_RESPONSE = {
    **PUBLISHED_PROPS,
    "identity": IDENTITY,
}
WITHDRAWN_RESPONSE = {
    **WITHDRAWN_PROPS,
    "identity": IDENTITY,
}
REQUEST_DATA = json.dumps(PROPS)


class TestSBOMS(TestCase):
    """
    Test Archivist SBOMS Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=2)
        self.mockstream = BytesIO(b"somelongstring")

    def test_SBOMS_upload(self):
        """
        Test attachment upload
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            sbom = self.arch.sboms.upload(self.mockstream)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBPATH}",),
                msg="UPLOAD method called incorrectly",
            )
            self.assertTrue(
                "headers" in kwargs,
                msg="UPLOAD no headers found",
            )
            headers = kwargs["headers"]
            self.assertTrue(
                "authorization" in headers,
                msg="UPLOAD no authorization found",
            )
            self.assertEqual(
                headers["authorization"],
                "Bearer authauthauth",
                msg="UPLOAD incorrect authorization",
            )
            self.assertTrue(
                headers["content-type"].startswith("multipart/form-data;"),
                msg="UPLOAD incorrect content-type",
            )
            self.assertTrue(
                kwargs["verify"],
                msg="UPLOAD method called incorrectly",
            )
            self.assertTrue(
                "data" in kwargs,
                msg="UPLOAD no data found",
            )
            fields = kwargs["data"].fields
            self.assertTrue(
                "sbom" in fields,
                msg="UPLOAD no field 'sbom' found",
            )
            self.assertEqual(
                fields["sbom"][0],
                "filename",
                msg="UPLOAD incorrect filename",
            )
            self.assertEqual(
                fields["sbom"][2],
                "text/xml",
                msg="UPLOAD incorrect filetype",
            )
            self.assertEqual(
                sbom,
                SBOM(**RESPONSE),
                msg="UPLOAD method called incorrectly",
            )
            self.assertEqual(
                sbom.dict(),
                RESPONSE,
                msg="UPLOAD method called incorrectly",
            )

    def test_SBOMS_download(self):
        """
        Test SBOM download
        """

        with mock.patch.object(self.arch._session, "get") as mock_get:

            def iter_content():
                i = 0

                def filedata(chunk_size=4096):  # pylint: disable=unused-argument
                    nonlocal i
                    while i < 4:
                        i += 1

                        if i == 2:
                            yield None

                        yield b"chunkofbytes"

                return filedata

            mock_get.return_value = MockResponse(
                200,
                iter_content=iter_content(),
                **RESPONSE,
            )
            with BytesIO() as fd:
                sbom = self.arch.sboms.download(IDENTITY, fd)
                args, kwargs = mock_get.call_args
                self.assertEqual(
                    args,
                    (f"url/{ROOT}/{SBOMS_SUBPATH}/{IDENTITY}",),
                    msg="DOWNLOAD method called incorrectly",
                )
                self.assertEqual(
                    kwargs,
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            "content-type": "application/json",
                        },
                        "stream": True,
                        "verify": True,
                    },
                    msg="DOWNLOAD method called incorrectly",
                )
                self.assertEqual(
                    sbom,
                    RESPONSE,
                    msg="DOWNLOAD method called incorrectly",
                )

    def test_sbom_metadata_read(self):
        """
        Test SBOM metadata reading
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            sbom = self.arch.sboms.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SBOMS_SUBPATH}/{IDENTITY}/{SBOMS_METADATA}"),),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "params": None,
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_sbom_publish(self):
        """
        Test SBOM publish
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            sbom = self.arch.sboms.publish(IDENTITY)
            self.assertEqual(
                tuple(mock_post.call_args),
                (
                    ((f"url/{ROOT}/{SBOMS_SUBPATH}/{IDENTITY}:{SBOMS_PUBLISH}"),),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "data": None,
                        "verify": True,
                    },
                ),
                msg="POST method called incorrectly",
            )

    def test_sbom_publish_with_confirmation(self):
        """
        Test sbom publication
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **PUBLISHED_RESPONSE)
            sbom = self.arch.sboms.publish(IDENTITY, confirm=True)
            self.assertEqual(
                sbom.dict(),
                PUBLISHED_RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_sbom_publish_with_confirmation_never_published(self):
        """
        Test publish confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
            ]
            with self.assertRaises(ArchivistUnpublishedError):
                sbom = self.arch.sboms.publish(IDENTITY, confirm=True)

    def test_sbom_withdraw(self):
        """
        Test SBOM withdraw
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            sbom = self.arch.sboms.withdraw(IDENTITY)
            self.assertEqual(
                tuple(mock_post.call_args),
                (
                    ((f"url/{ROOT}/{SBOMS_SUBPATH}/{IDENTITY}:{SBOMS_WITHDRAW}"),),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                        },
                        "data": None,
                        "verify": True,
                    },
                ),
                msg="POST method called incorrectly",
            )

    def test_sbom_withdraw_with_confirmation(self):
        """
        Test sbom withdrawal
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.return_value = MockResponse(200, **WITHDRAWN_RESPONSE)
            sbom = self.arch.sboms.withdraw(IDENTITY, confirm=True)
            self.assertEqual(
                sbom.dict(),
                WITHDRAWN_RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_sbom_withdraw_with_confirmation_never_withdrawn(self):
        """
        Test withdawan confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
                MockResponse(200, **RESPONSE),
            ]
            with self.assertRaises(ArchivistUnwithdrawnError):
                sbom = self.arch.sboms.withdraw(IDENTITY, confirm=True)

    def test_sboms_list(self):
        """
        Test sboms listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                sboms=[
                    RESPONSE,
                ],
            )

            sboms = list(self.arch.sboms.list())
            self.assertEqual(
                len(sboms),
                1,
                msg="incorrect number of sboms",
            )
            for sbom in sboms:
                self.assertEqual(
                    sbom,
                    SBOM(**RESPONSE),
                    msg="Incorrect sbom listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/{SUBPATH}/{SBOMS_WILDCARD}",),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_sboms_list_with_query(self):
        """
        Test sboms listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                sboms=[
                    RESPONSE,
                ],
            )

            sboms = list(
                self.arch.sboms.list(
                    metadata={
                        "lifecycle_status": "ACTIVE",
                        "version": "10.0.2",
                    },
                )
            )
            self.assertEqual(
                len(sboms),
                1,
                msg="incorrect number of sboms",
            )
            for sbom in sboms:
                self.assertEqual(
                    sbom,
                    SBOM(**RESPONSE),
                    msg="Incorrect sbom listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"url/{ROOT}/{SUBPATH}/{SBOMS_WILDCARD}"
                                "?lifecycle_status=ACTIVE"
                                "&version=10.0.2"
                            ),
                        ),
                        {
                            "headers": {
                                "content-type": "application/json",
                                "authorization": "Bearer authauthauth",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )
