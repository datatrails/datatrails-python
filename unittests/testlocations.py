"""
Test archivist
"""

from json import loads as json_loads
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    LOCATIONS_SUBPATH,
    LOCATIONS_LABEL,
)
from archivist.errors import ArchivistBadRequestError

from .mock_response import MockResponse


# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

PROPS = {
    "display_name": "Macclesfield, Cheshire",
    "description": "Manufacturing site, North West England, Macclesfield, Cheshire",
    "latitude": "53.2546799",
    "longitude": "-2.1213956,14.54",
}
ATTRS = {
    "director": "John Smith",
    "address": "Bridgewater, Somerset",
    "facility_type": "Manufacture",
    "support_email": "support@macclesfield.com",
    "support_phone": "123 456 789",
}

IDENTITY = f"{LOCATIONS_LABEL}/xxxxxxxx"
SUBPATH = f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}"

RESPONSE = {
    **PROPS,
    "identity": IDENTITY,
    "attributes": ATTRS,
}
REQUEST = {
    **PROPS,
    "attributes": ATTRS,
}


class TestLocations(TestCase):
    """
    Test Archivist Locations Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def test_locations_str(self):
        """
        Test locations str
        """
        self.assertEqual(
            str(self.arch.locations),
            "LocationsClient(url)",
            msg="Incorrect str",
        )

    def test_locations_create(self):
        """
        Test location creation
        """
        with mock.patch.object(self.arch._session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            location = self.arch.locations.create(PROPS, attrs=ATTRS)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBPATH}",),
                msg="CREATE method args called incorrectly",
            )
            kwargs["data"] = json_loads(kwargs["data"])
            self.assertEqual(
                kwargs,
                {
                    "data": REQUEST,
                    "headers": {
                        "content-type": "application/json",
                        "authorization": "Bearer authauthauth",
                    },
                    "verify": True,
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                location,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_locations_read(self):
        """
        Test asset reading
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            asset = self.arch.locations.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{LOCATIONS_SUBPATH}/{IDENTITY}"),),
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

    def test_locations_read_with_error(self):
        """
        Test read method with error
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(400)
            with self.assertRaises(ArchivistBadRequestError):
                resp = self.arch.locations.read(IDENTITY)

    def test_locations_count(self):
        """
        Test location counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                locations=[
                    RESPONSE,
                ],
            )

            count = self.arch.locations.count()
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBPATH}" "?page_size=1"),),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )
            self.assertEqual(
                count,
                1,
                msg="Incorrect count",
            )

    def test_locations_count_with_props_query(self):
        """
        Test location counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                locations=[
                    RESPONSE,
                ],
            )

            count = self.arch.locations.count(
                props={"display_name": "Macclesfield, Cheshire"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{SUBPATH}"
                            "?page_size=1"
                            "&display_name=Macclesfield, Cheshire"
                        ),
                    ),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_locations_count_with_attrs_query(self):
        """
        Test location counting
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                locations=[
                    RESPONSE,
                ],
            )

            count = self.arch.locations.count(
                attrs={"director": "John Smith"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (
                        (
                            f"url/{ROOT}/{SUBPATH}"
                            "?page_size=1"
                            "&attributes.director=John Smith"
                        ),
                    ),
                    {
                        "headers": {
                            "content-type": "application/json",
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "verify": True,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_locations_list(self):
        """
        Test location listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                locations=[
                    RESPONSE,
                ],
            )

            locations = list(self.arch.locations.list())
            self.assertEqual(
                len(locations),
                1,
                msg="incorrect number of locations",
            )
            for location in locations:
                self.assertEqual(
                    location,
                    RESPONSE,
                    msg="Incorrect location listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/{SUBPATH}",),
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

    def test_locations_list_with_query(self):
        """
        Test location listing
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                locations=[
                    RESPONSE,
                ],
            )

            locations = list(
                self.arch.locations.list(
                    props={"display_name": "Macclesfield, Cheshire"},
                    attrs={"director": "John Smith"},
                )
            )
            self.assertEqual(
                len(locations),
                1,
                msg="incorrect number of locations",
            )
            for location in locations:
                self.assertEqual(
                    location,
                    RESPONSE,
                    msg="Incorrect location listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (
                            (
                                f"url/{ROOT}/{SUBPATH}"
                                "?attributes.director=John Smith"
                                "&display_name=Macclesfield, Cheshire"
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

    def test_locations_read_by_signature(self):
        """
        Test location read_by_signature
        """
        with mock.patch.object(self.arch._session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                locations=[
                    RESPONSE,
                ],
            )

            location = self.arch.locations.read_by_signature()
            self.assertEqual(
                location,
                RESPONSE,
                msg="Incorrect location listed",
            )

            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (f"url/{ROOT}/{SUBPATH}?page_size=2",),
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
