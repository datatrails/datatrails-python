"""
Test SBOMS
"""

from io import BytesIO
from os import environ
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
from archivist.errors import (
    ArchivistNotFoundError,
    ArchivistUnpublishedError,
    ArchivistUnwithdrawnError,
)
from archivist.logger import set_logger
from archivist.sbommetadata import SBOM

from .mock_response import MockResponse

# pylint: disable=protected-access
# pylint: disable=unused-variable

if "TEST_DEBUG" in environ and environ["TEST_DEBUG"]:
    set_logger(environ["TEST_DEBUG"])

IDENTITY = f"{SBOMS_LABEL}/c3da0d3a-32bf-4f5f-a8c6-b342a8356480"
PROPS = {
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
    "rkvst_link": "",
}
PUBLISHED_PROPS = {**PROPS, **{"published_date": "2021-11-11T17:02:06Z"}}
WITHDRAWN_PROPS = {**PROPS, **{"withdrawn_date": "2021-11-11T17:02:06Z"}}

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


class TestSBOMS(TestCase):
    """
    Test Archivist SBOMS Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=1)
        self.mockstream = BytesIO(b"somelongstring")

    def test_sboms_str(self):
        """
        Test sboms str
        """
        self.assertEqual(
            str(self.arch.sboms),
            "SBOMSClient(url)",
            msg="Incorrect str",
        )

    def test_sboms_upload_spdx(self):
        """
        Test attachment upload
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            sbom = self.arch.sboms.upload(
                self.mockstream,
                params={
                    "sbomType": "spdx-tag",
                    "component": "spdx-test-component",
                    "version": "v0.0.1",
                },
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBPATH}",),
                msg="UPLOAD method called incorrectly",
            )
            self.assertEqual(
                "headers" in kwargs,
                True,
                msg="UPLOAD no headers found",
            )
            headers = kwargs["headers"]
            self.assertEqual(
                "authorization" in headers,
                True,
                msg="UPLOAD no authorization found",
            )
            params = kwargs["params"]
            self.assertEqual(
                params,
                {
                    "sbomType": "spdx-tag",
                    "component": "spdx-test-component",
                    "version": "v0.0.1",
                },
                msg="Params did not contain expected values",
            )
            self.assertEqual(
                headers["authorization"],
                "Bearer authauthauth",
                msg="UPLOAD incorrect authorization",
            )
            self.assertEqual(
                headers["content-type"].startswith("multipart/form-data;"),
                True,
                msg="UPLOAD incorrect content-type",
            )
            self.assertEqual(
                kwargs["verify"],
                True,
                msg="UPLOAD method called incorrectly",
            )
            self.assertEqual(
                "data" in kwargs,
                True,
                msg="UPLOAD no data found",
            )
            fields = kwargs["data"].fields
            self.assertEqual(
                "sbom" in fields,
                True,
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

    def test_sboms_upload(self):
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
            self.assertEqual(
                "headers" in kwargs,
                True,
                msg="UPLOAD no headers found",
            )
            headers = kwargs["headers"]
            self.assertEqual(
                "authorization" in headers,
                True,
                msg="UPLOAD no authorization found",
            )
            self.assertEqual(
                headers["authorization"],
                "Bearer authauthauth",
                msg="UPLOAD incorrect authorization",
            )
            self.assertEqual(
                headers["content-type"].startswith("multipart/form-data;"),
                True,
                msg="UPLOAD incorrect content-type",
            )
            self.assertEqual(
                kwargs["verify"],
                True,
                msg="UPLOAD method called incorrectly",
            )
            self.assertEqual(
                "data" in kwargs,
                True,
                msg="UPLOAD no data found",
            )
            fields = kwargs["data"].fields
            self.assertEqual(
                "sbom" in fields,
                True,
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

    def test_sbom_upload_with_confirmation_never_uploaded(self):
        """
        Test upload confirmation
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                ArchivistNotFoundError("sbom not found"),
                ArchivistNotFoundError("sbom not found"),
                ArchivistNotFoundError("sbom not found"),
                ArchivistNotFoundError("sbom not found"),
                ArchivistNotFoundError("sbom not found"),
                ArchivistNotFoundError("sbom not found"),
                ArchivistNotFoundError("sbom not found"),
                ArchivistNotFoundError("sbom not found"),
                ArchivistNotFoundError("sbom not found"),
                ArchivistNotFoundError("sbom not found"),
            ]
            with self.assertRaises(ArchivistNotFoundError):
                sbom = self.arch.sboms.upload(self.mockstream, confirm=True)

    def test_sboms_download(self):
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
                        },
                        "stream": True,
                        "verify": True,
                        "params": None,
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
                            "authorization": "Bearer authauthauth",
                        },
                        "json": None,
                        "verify": True,
                    },
                ),
                msg="POST method called incorrectly",
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
                            "authorization": "Bearer authauthauth",
                        },
                        "json": None,
                        "verify": True,
                    },
                ),
                msg="POST method called incorrectly",
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
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {},
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_sboms_list_with_params(self):
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
                        ((f"url/{ROOT}/{SUBPATH}/{SBOMS_WILDCARD}"),),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {
                                "lifecycle_status": "ACTIVE",
                                "version": "10.0.2",
                            },
                            "verify": True,
                        },
                    ),
                    msg="GET method called incorrectly",
                )


class TestSBOMSConfirm(TestCase):
    """
    Test Archivist SBOMS Create method with expected confirmation
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth", max_time=100)
        self.mockstream = BytesIO(b"somelongstring")

    def test_sbom_upload_with_confirmation(self):
        """
        Test sbom upload
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE),
            ]
            sbom = self.arch.sboms.upload(self.mockstream, confirm=True)
            self.assertEqual(
                sbom.dict(),
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_sbom_upload_with_confirmation_and_privacy(self):
        """
        Test sbom upload
        """
        with mock.patch.object(
            self.arch._session, "post"
        ) as mock_post, mock.patch.object(self.arch._session, "get") as mock_get:
            mock_post.return_value = MockResponse(200, **RESPONSE)
            mock_get.side_effect = [
                MockResponse(200, **RESPONSE),
            ]
            sbom = self.arch.sboms.upload(
                self.mockstream, confirm=True, params={"privacy": "PUBLIC"}
            )
            self.assertEqual(
                sbom.dict(),
                RESPONSE,
                msg="CREATE method called incorrectly",
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
