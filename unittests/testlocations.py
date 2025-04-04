"""
Test locations
"""

from unittest import TestCase, mock

from archivist.about import __version__ as VERSION
from archivist.archivist import Archivist
from archivist.constants import (
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    LOCATIONS_LABEL,
    LOCATIONS_SUBPATH,
    ROOT,
    USER_AGENT,
    USER_AGENT_PREFIX,
)
from archivist.errors import ArchivistBadRequestError, ArchivistNotFoundError
from archivist.locations import Location

from .mock_response import MockResponse

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

SIGNATURE_PROPS = {
    "display_name": "Macclesfield, Cheshire",
}
SIGNATURE_ATTRS = {
    "director": "John Smith",
}
SIGNATURE = {
    **SIGNATURE_PROPS,
    "attributes": SIGNATURE_ATTRS,
}

IDENTITY = f"{LOCATIONS_LABEL}/xxxxxxxx"
SUBPATH = f"{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}"

BARE_ATTRS = {
    "director": "John Smith",
    "address": "Bridgewater, Somerset",
    "facility_type": "Manufacture",
    "support_email": "support@macclesfield.com",
    "support_phone": "123 456 789",
}
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

REQUEST = {
    "display_name": "Macclesfield, Cheshire",
    "description": "Manufacturing site, North West England, Macclesfield, Cheshire",
    "latitude": "53.2546799",
    "longitude": "-2.1213956,14.54",
    "attributes": {
        "director": "John Smith",
        "address": "Bridgewater, Somerset",
        "facility_type": "Manufacture",
        "support_email": "support@macclesfield.com",
        "support_phone": "123 456 789",
    },
}
RESPONSE = {
    "identity": IDENTITY,
    "display_name": "Macclesfield, Cheshire",
    "description": "Manufacturing site, North West England, Macclesfield, Cheshire",
    "latitude": "53.2546799",
    "longitude": "-2.1213956,14.54",
    "attributes": {
        "director": "John Smith",
        "address": "Bridgewater, Somerset",
        "facility_type": "Manufacture",
        "support_email": "support@macclesfield.com",
        "support_phone": "123 456 789",
    },
}
REQUEST_EXISTS = {
    "selector": [
        "display_name",
        {
            "attributes": [
                "director",
            ],
        },
    ],
    "display_name": "Macclesfield, Cheshire",
    "description": "Manufacturing site, North West England, Macclesfield, Cheshire",
    "latitude": "53.2546799",
    "longitude": "-2.1213956,14.54",
    "attributes": {
        "director": "John Smith",
        "address": "Bridgewater, Somerset",
        "facility_type": "Manufacture",
        "support_email": "support@macclesfield.com",
        "support_phone": "123 456 789",
    },
}
REQUEST_EXISTS_SELECTOR_NOATTRS = {
    "selector": [
        "display_name",
    ],
    "display_name": "Macclesfield, Cheshire",
    "description": "Manufacturing site, North West England, Macclesfield, Cheshire",
    "latitude": "53.2546799",
    "longitude": "-2.1213956,14.54",
    "attributes": {
        "director": "John Smith",
        "address": "Bridgewater, Somerset",
        "facility_type": "Manufacture",
        "support_email": "support@macclesfield.com",
        "support_phone": "123 456 789",
    },
}


class TestLocation(TestCase):
    """
    Test Archivist Location
    """

    maxDiff = None

    def test_location_name(self):
        """
        Test location name
        """
        self.assertEqual(
            Location(x="something").name,
            None,
            msg="Incorrect name",
        )
        self.assertEqual(
            Location(display_name="something").name,
            "something",
            msg="Incorrect name",
        )


class TestLocations(TestCase):
    """
    Test Archivist Locations Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()

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
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **RESPONSE)

            location = self.arch.locations.create(PROPS, attrs=ATTRS)
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBPATH}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                location,
                RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_locations_create_if_not_exists_existing_location(self):
        """
        Test location creation
        """
        with (
            mock.patch.object(self.arch.session, "get") as mock_get,
            mock.patch.object(self.arch.session, "post") as mock_post,
        ):
            mock_get.return_value = MockResponse(
                200,
                locations=[
                    RESPONSE,
                ],
            )
            mock_post.return_value = MockResponse(200, **RESPONSE)
            location, existed = self.arch.locations.create_if_not_exists(
                REQUEST_EXISTS,
            )
            mock_post.assert_not_called()
            self.assertEqual(
                existed,
                True,
                msg="Incorrect existed bool",
            )
            self.assertEqual(
                location,
                RESPONSE,
                msg="Incorrect location listed",
            )

            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (f"url/{ROOT}/{SUBPATH}",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": {
                            "page_size": 2,
                            "display_name": "Macclesfield, Cheshire",
                            "attributes.director": "John Smith",
                        },
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_locations_create_if_not_exists_nonexistent_location(self):
        """
        Test location creation
        """
        with (
            mock.patch.object(self.arch.session, "get") as mock_get,
            mock.patch.object(self.arch.session, "post") as mock_post,
        ):
            mock_get.side_effect = ArchivistNotFoundError
            mock_post.return_value = MockResponse(200, **RESPONSE)
            location, existed = self.arch.locations.create_if_not_exists(
                REQUEST_EXISTS,
            )
            mock_get.assert_called_once()
            mock_post.assert_called_once()
            self.assertEqual(
                location,
                RESPONSE,
                msg="Incorrect location listed",
            )
            self.assertEqual(
                existed,
                False,
                msg="Incorrect existed bool",
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBPATH}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="CREATE method kwargs called incorrectly",
            )

    def test_locations_create_if_not_exists_nonexistent_location_selector_noattributes(
        self,
    ):
        """
        Test location creation
        """
        with (
            mock.patch.object(self.arch.session, "get") as mock_get,
            mock.patch.object(self.arch.session, "post") as mock_post,
        ):
            mock_get.side_effect = ArchivistNotFoundError
            mock_post.return_value = MockResponse(200, **RESPONSE)
            location, existed = self.arch.locations.create_if_not_exists(
                REQUEST_EXISTS_SELECTOR_NOATTRS,
            )
            mock_get.assert_called_once()
            mock_post.assert_called_once()
            self.assertEqual(
                location,
                RESPONSE,
                msg="Incorrect location listed",
            )
            self.assertEqual(
                existed,
                False,
                msg="Incorrect existed bool",
            )
            args, kwargs = mock_post.call_args
            self.assertEqual(
                args,
                (f"url/{ROOT}/{SUBPATH}",),
                msg="CREATE method args called incorrectly",
            )
            self.assertEqual(
                kwargs,
                {
                    "json": REQUEST,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                        USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                    },
                },
                msg="CREATE method kwargs called incorrectly",
            )

    def test_locations_read(self):
        """
        Test asset reading
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **RESPONSE)

            self.arch.locations.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{LOCATIONS_SUBPATH}/{IDENTITY}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_locations_read_with_error(self):
        """
        Test read method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(400)
            with self.assertRaises(ArchivistBadRequestError):
                self.arch.locations.read(IDENTITY)

    def test_locations_count(self):
        """
        Test location counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
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
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": {"page_size": 1},
                    },
                ),
                msg="GET method called incorrectly",
            )
            self.assertEqual(
                count,
                1,
                msg="Incorrect count",
            )

    def test_locations_count_with_props_params(self):
        """
        Test location counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                locations=[
                    RESPONSE,
                ],
            )

            self.arch.locations.count(
                props={"display_name": "Macclesfield, Cheshire"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": {
                            "page_size": 1,
                            "display_name": "Macclesfield, Cheshire",
                        },
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_locations_count_with_attrs_params(self):
        """
        Test location counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                locations=[
                    RESPONSE,
                ],
            )

            self.arch.locations.count(
                attrs={"director": "John Smith"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": {
                            "page_size": 1,
                            "attributes.director": "John Smith",
                        },
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_locations_list(self):
        """
        Test location listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
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
                                "authorization": "Bearer authauthauth",
                                USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                            },
                            "params": {},
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_locations_list_with_params(self):
        """
        Test location listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
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
                        ((f"url/{ROOT}/{SUBPATH}"),),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                                USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                            },
                            "params": {
                                "attributes.director": "John Smith",
                                "display_name": "Macclesfield, Cheshire",
                            },
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_locations_read_by_signature(self):
        """
        Test location read_by_signature
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
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
                    (f"url/{ROOT}/{SUBPATH}",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            USER_AGENT: f"{USER_AGENT_PREFIX}{VERSION}",
                        },
                        "params": {"page_size": 2},
                    },
                ),
                msg="GET method called incorrectly",
            )
