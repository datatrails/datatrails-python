'''
Test archivist
'''

import json
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
from archivist.locations import DEFAULT_PAGE_SIZE

from .mock_response import MockResponse


# pylint: disable=missing-docstring
# pylint: disable=unnecessary-comprehension
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
    "support_phone": "123 456 789"
}

IDENTITY = f'{LOCATIONS_LABEL}/xxxxxxxx'
SUBPATH = f'{LOCATIONS_SUBPATH}/{LOCATIONS_LABEL}'

RESPONSE = {
    **PROPS,
    'identity': IDENTITY,
    'attributes': ATTRS,
}
REQUEST = {
    **PROPS,
    'attributes': ATTRS,
}
REQUEST_DATA = json.dumps(REQUEST)


class TestLocations(TestCase):
    '''
    Test Archivist Locations Create method
    '''
    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", auth="authauthauth")

    @mock.patch('requests.post')
    def test_locations_create(self, mock_post):
        '''
        Test location creation
        '''
        mock_post.return_value = MockResponse(200, **RESPONSE)

        location = self.arch.locations.create(PROPS, attrs=ATTRS)
        self.assertEqual(
            tuple(mock_post.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{SUBPATH}"
                    ),
                ),
                {
                    'data': REQUEST_DATA,
                    'headers': {
                        'content-type': 'application/json',
                        'authorization': "Bearer authauthauth",
                    },
                    'verify': True,
                    'cert': None,
                },
            ),
            msg="CREATE method called incorrectly",
        )
        self.assertEqual(
            location,
            RESPONSE,
            msg="CREATE method called incorrectly",
        )

    @mock.patch('requests.get')
    def test_locations_read(self, mock_get):
        '''
        Test asset reading
        '''
        mock_get.return_value = MockResponse(200, **RESPONSE)

        asset = self.arch.locations.read(IDENTITY)
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{LOCATIONS_SUBPATH}/{IDENTITY}"
                    ),
                ),
                {
                    'headers': {
                        'content-type': 'application/json',
                        'authorization': "Bearer authauthauth",
                    },
                    'verify': True,
                    'cert': None,
                },
            ),
            msg="GET method called incorrectly",
        )

    @mock.patch('requests.get')
    def test_locations_read_with_error(self, mock_get):
        '''
        Test read method with error
        '''
        mock_get.return_value = MockResponse(400)
        with self.assertRaises(ArchivistBadRequestError):
            resp = self.arch.locations.read(IDENTITY)

    @mock.patch('requests.get')
    def test_locations_count(self, mock_get):
        '''
        Test location counting
        '''
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
                (
                    (
                        f"url/{ROOT}/{SUBPATH}"
                        "?page_size=1"
                    ),
                ),
                {
                    'headers': {
                        'content-type': 'application/json',
                        'authorization': "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: 'true',
                    },
                    'verify': True,
                    'cert': None,
                },
            ),
            msg="GET method called incorrectly",
        )
        self.assertEqual(
            count,
            1,
            msg="Incorrect count",
        )

    @mock.patch('requests.get')
    def test_locations_count_with_props_query(self, mock_get):
        '''
        Test location counting
        '''
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
                    'headers': {
                        'content-type': 'application/json',
                        'authorization': "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: 'true',
                    },
                    'verify': True,
                    'cert': None,
                },
            ),
            msg="GET method called incorrectly",
        )

    @mock.patch('requests.get')
    def test_locations_count_with_attrs_query(self, mock_get):
        '''
        Test location counting
        '''
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
                    'headers': {
                        'content-type': 'application/json',
                        'authorization': "Bearer authauthauth",
                        HEADERS_REQUEST_TOTAL_COUNT: 'true',
                    },
                    'verify': True,
                    'cert': None,
                },
            ),
            msg="GET method called incorrectly",
        )

    @mock.patch('requests.get')
    def test_locations_list(self, mock_get):
        '''
        Test location listing
        '''
        mock_get.return_value = MockResponse(
            200,
            locations=[
                RESPONSE,
            ],
        )

        listing = self.arch.locations.list()
        locations = [a for a in listing]
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
                    (f"url/{ROOT}/{SUBPATH}?page_size={DEFAULT_PAGE_SIZE}",),
                    {
                        'headers': {
                            'content-type': 'application/json',
                            'authorization': "Bearer authauthauth",
                        },
                        'verify': True,
                        'cert': None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    @mock.patch('requests.get')
    def test_locations_list_with_query(self, mock_get):
        '''
        Test location listing
        '''
        mock_get.return_value = MockResponse(
            200,
            locations=[
                RESPONSE,
            ],
        )

        listing = self.arch.locations.list(
            props={"display_name": "Macclesfield, Cheshire"},
            attrs={"director": "John Smith"},
        )
        locations = [a for a in listing]
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
                            f"?page_size={DEFAULT_PAGE_SIZE}"
                            "&attributes.director=John Smith"
                            "&display_name=Macclesfield, Cheshire"
                        ),
                    ),
                    {
                        'headers': {
                            'content-type': 'application/json',
                            'authorization': "Bearer authauthauth",
                        },
                        'verify': True,
                        'cert': None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    @mock.patch('requests.get')
    def test_locations_read_by_signature(self, mock_get):
        '''
        Test location read_by_signature
        '''
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
                    'headers': {
                        'content-type': 'application/json',
                        'authorization': "Bearer authauthauth",
                    },
                    'verify': True,
                    'cert': None,
                },
            ),
            msg="GET method called incorrectly",
        )
