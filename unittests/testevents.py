'''
Test archivist
'''

import json
from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.constants import (
    ROOT,
    ASSETS_LABEL,
    ASSETS_WILDCARD,
    ASSETS_SUBPATH,
    ATTACHMENTS_LABEL,
    EVENTS_LABEL,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
)
from archivist.errors import ArchivistUnconfirmedError
from archivist.events import Event, DEFAULT_PAGE_SIZE

from .mock_response import MockResponse

# pylint: disable=missing-docstring
# pylint: disable=unnecessary-comprehension
# pylint: disable=unused-variable

ASSET_ID = f"{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"

PRIMARY_IMAGE = {
    "arc_attachment_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "arc_display_name": "an attachment 2",
    "arc_hash_value": "042aea10a0f14f2d391373599be69d53a75dde9951fc3d3cd10b6100aa7a9f24",
    "arc_hash_alg": "sha256",
}
SECONDARY_IMAGE = {
    "arc_attachment_identity": f"{ATTACHMENTS_LABEL}/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "arc_display_name": "an attachment 1",
    "arc_hash_value": "jnwpjocoqsssnundwlqalsqiiqsqp;lpiwpldkndwwlskqaalijopjkokkkojijl",
    "arc_hash_alg": "sha256",
}
PRINCIPAL_DECLARED = {
    "issuer": "idp.synsation.io/1234",
    "subject": "phil.b",
    "email": "phil.b@synsation.io",
    "display_name": "Declared",
}
PRINCIPAL_ACCEPTED = {
    "issuer": "idp.synsation.io/1234",
    "subject": "phil.b",
    "email": "phil.b@synsation.io",
    "display_name": "Accepted",
}
PROPS = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_accepted": PRINCIPAL_ACCEPTED,
}
PROPS_WITH_NO_TIMESTAMP = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "principal_accepted": PRINCIPAL_ACCEPTED,
}
PROPS_WITH_TIMESTAMP_ACCEPTED = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "timestamp_accepted": "2021-04-08T14:44:19Z",
    "principal_accepted": PRINCIPAL_ACCEPTED,
}
PROPS_WITH_PRINCIPAL_DECLARED = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "timestamp_declared": "2019-11-27T14:44:19Z",
    "principal_declared": PRINCIPAL_DECLARED,
}
PROPS_WITH_NO_PRINCIPAL = {
    "operation": "Attach",
    "behaviour": "Attachments",
    "timestamp_declared": "2019-11-27T14:44:19Z",
}

EVENT_ATTRS = {
    "arc_append_attachments": [
        SECONDARY_IMAGE,
        PRIMARY_IMAGE,
    ],
}
ASSET_ATTRS = {
    "external_container": 'assets/xxxx',
}

IDENTITY = f'{ASSET_ID}/{EVENTS_LABEL}/xxxxxxxxxxxxxxxxxxxx'

REQUEST = {
    **PROPS,
    'event_attributes': EVENT_ATTRS,
}
REQUEST_DATA = json.dumps(REQUEST)

REQUEST_WITH_ASSET_ATTRS = {
    **REQUEST,
    'asset_attributes': ASSET_ATTRS,
}
REQUEST_DATA_WITH_ASSET_ATTRS = json.dumps(REQUEST_WITH_ASSET_ATTRS)

REQUEST_WITH_NO_PRINCIPAL = {
    **PROPS_WITH_NO_PRINCIPAL,
    'event_attributes': EVENT_ATTRS,
}
REQUEST_WITH_NO_PRINCIPAL_DATA = json.dumps(REQUEST_WITH_NO_PRINCIPAL)

RESPONSE = {
    **PROPS,
    'identity': IDENTITY,
    'event_attributes': EVENT_ATTRS,
    'confirmation_status': 'CONFIRMED',
}
RESPONSE_WITH_ASSET_ATTRS = {
    **RESPONSE,
    'asset_attributes': ASSET_ATTRS,
}
RESPONSE_NO_CONFIRMATION = {
    **PROPS,
    'identity': IDENTITY,
    'event_attributes': EVENT_ATTRS,
}
RESPONSE_PENDING = {
    **PROPS,
    'identity': IDENTITY,
    'event_attributes': EVENT_ATTRS,
    'confirmation_status': 'PENDING',
}
RESPONSE_FAILED = {
    **PROPS,
    'identity': IDENTITY,
    'event_attributes': EVENT_ATTRS,
    'confirmation_status': 'FAILED',
}
RESPONSE_WITH_NO_TIMESTAMP = {
    **PROPS_WITH_NO_TIMESTAMP,
    'identity': IDENTITY,
    'event_attributes': EVENT_ATTRS,
    'confirmation_status': 'CONFIRMED',
}
RESPONSE_WITH_TIMESTAMP_ACCEPTED = {
    **PROPS_WITH_TIMESTAMP_ACCEPTED,
    'identity': IDENTITY,
    'event_attributes': EVENT_ATTRS,
    'confirmation_status': 'CONFIRMED',
}

RESPONSE_WITH_PRINCIPAL_DECLARED = {
    **PROPS_WITH_PRINCIPAL_DECLARED,
    'identity': IDENTITY,
    'event_attributes': EVENT_ATTRS,
    'confirmation_status': 'CONFIRMED',
}

RESPONSE_WITH_NO_PRINCIPAL = {
    **PROPS_WITH_NO_PRINCIPAL,
    'identity': IDENTITY,
    'event_attributes': EVENT_ATTRS,
    'confirmation_status': 'CONFIRMED',
}


class TestEvent(TestCase):
    '''
    Test Archivist Events Create method
    '''
    maxDiff = None

    def test_event_who_accepted(self):
        event = Event(**RESPONSE)
        self.assertEqual(
            event.who,
            "Accepted",
            msg="Incorrect who",
        )

    def test_event_who_none(self):
        event = Event(**RESPONSE_WITH_NO_PRINCIPAL)
        self.assertEqual(
            event.who,
            None,
            msg="who should be None",
        )

    def test_event_who_declared(self):
        event = Event(**RESPONSE_WITH_PRINCIPAL_DECLARED)
        self.assertEqual(
            event.who,
            "Declared",
            msg="Incorrect who",
        )

    def test_event_when_declared(self):
        event = Event(**RESPONSE)
        self.assertEqual(
            event.when,
            "2019-11-27T14:44:19Z",
            msg="Incorrect when",
        )

    def test_event_when_accepted(self):
        event = Event(**RESPONSE_WITH_TIMESTAMP_ACCEPTED)
        self.assertEqual(
            event.when,
            "2021-04-08T14:44:19Z",
            msg="Incorrect when",
        )

    def test_event_when_none(self):
        event = Event(**RESPONSE_WITH_NO_TIMESTAMP)
        self.assertEqual(
            event.when,
            None,
            msg="Incorrect when",
        )


class TestEvents(TestCase):
    '''
    Test Archivist Events Create method
    '''
    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", auth="authauthauth")

    @mock.patch('requests.post')
    def test_events_create(self, mock_post):
        '''
        Test event creation
        '''
        mock_post.return_value = MockResponse(200, **RESPONSE)

        event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=False)
        self.assertEqual(
            tuple(mock_post.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                    ),
                ),
                {
                    "data": REQUEST_DATA,
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
            event,
            RESPONSE,
            msg="CREATE method called incorrectly",
        )

    @mock.patch('requests.post')
    def test_events_create_with_asset_attrs(self, mock_post):
        '''
        Test event creation
        '''
        mock_post.return_value = MockResponse(200, **RESPONSE_WITH_ASSET_ATTRS)

        event = self.arch.events.create(
            ASSET_ID,
            PROPS,
            EVENT_ATTRS,
            asset_attrs=ASSET_ATTRS,
            confirm=False,
        )
        self.assertEqual(
            tuple(mock_post.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                    ),
                ),
                {
                    "data": REQUEST_DATA_WITH_ASSET_ATTRS,
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
            event,
            RESPONSE_WITH_ASSET_ATTRS,
            msg="CREATE method called incorrectly",
        )

    @mock.patch('archivist.events.sleep')
    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_events_create_with_confirmation(self, mock_post, mock_get, mock_sleep):
        '''
        Test event creation
        '''
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.return_value = MockResponse(200, **RESPONSE)

        event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)
        self.assertEqual(
            mock_sleep.call_args_list,
            [],
            msg="Incorrect call to sleep",
        )
        self.assertEqual(
            event,
            RESPONSE,
            msg="CREATE method called incorrectly",
        )

    @mock.patch('archivist.events.sleep')
    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_events_create_with_confirmation_no_confirmed_status(
            self,
            mock_post,
            mock_get,
            mock_sleep,
    ):
        '''
        Test asset confirmation
        '''
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.return_value = MockResponse(200, **RESPONSE_NO_CONFIRMATION)

        with self.assertRaises(ArchivistUnconfirmedError):
            event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)

        self.assertEqual(
            mock_sleep.call_args_list,
            [],
            msg="Incorrect call to sleep",
        )

    @mock.patch('archivist.events.sleep')
    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_events_create_with_confirmation_pending_status(
            self,
            mock_post,
            mock_get,
            mock_sleep,
    ):
        '''
        Test asset confirmation
        '''
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.side_effect =[
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE),
        ]
        event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)
        self.assertEqual(
            event,
            RESPONSE,
            msg="CREATE method called incorrectly",
        )
        self.assertEqual(
            mock_sleep.call_args_list,
            [mock.call(1.0)],
            msg="Incorrect call to sleep",
        )

    @mock.patch('archivist.events.sleep')
    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_events_create_with_confirmation_failed_status(
            self,
            mock_post,
            mock_get,
            mock_sleep,
    ):
        '''
        Test asset confirmation
        '''
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.side_effect =[
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_FAILED),
        ]
        with self.assertRaises(ArchivistUnconfirmedError):
            event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)

        self.assertEqual(
            mock_sleep.call_args_list,
            [mock.call(1.0)],
            msg="Incorrect call to sleep",
        )

    @mock.patch('archivist.events.sleep')
    @mock.patch('requests.get')
    @mock.patch('requests.post')
    def test_events_create_with_confirmation_always_pending_status(
            self,
            mock_post,
            mock_get,
            mock_sleep,
    ):
        '''
        Test asset confirmation
        '''
        mock_post.return_value = MockResponse(200, **RESPONSE)
        mock_get.side_effect =[
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_PENDING),
            MockResponse(200, **RESPONSE_PENDING),
        ]
        self.arch.events.timeout = 5
        with self.assertRaises(ArchivistUnconfirmedError):
            event = self.arch.events.create(ASSET_ID, PROPS, EVENT_ATTRS, confirm=True)

        self.assertEqual(
            mock_sleep.call_args_list,
            [mock.call(1.0), mock.call(1.25), mock.call(1.5625), mock.call(1.953125)],
            msg="Incorrect call to sleep",
        )

    @mock.patch('requests.get')
    def test_events_read(self, mock_get):
        '''
        Test event counting
        '''
        mock_get.return_value = MockResponse(200, **RESPONSE)

        event = self.arch.events.read(IDENTITY)
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
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
        self.assertEqual(
            event,
            RESPONSE,
            msg="GET method called incorrectly",
        )

    @mock.patch('requests.get')
    def test_events_read_with_no_principal(self, mock_get):
        '''
        Test event counting
        '''
        mock_get.return_value = MockResponse(200, **RESPONSE)

        event = self.arch.events.read(IDENTITY)
        self.assertEqual(
            event,
            RESPONSE,
            msg="GET method called incorrectly",
        )

    @mock.patch('requests.get')
    def test_events_count(self, mock_get):
        '''
        Test event counting
        '''
        mock_get.return_value = MockResponse(
            200,
            headers={HEADERS_TOTAL_COUNT: 1},
            events=[
                RESPONSE,
            ],
        )

        count = self.arch.events.count(asset_id=ASSET_ID)
        self.assertEqual(
            count,
            1,
            msg="Incorrect count",
        )
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
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

    @mock.patch('requests.get')
    def test_events_count_with_props_query(self, mock_get):
        '''
        Test event counting
        '''
        mock_get.return_value = MockResponse(
            200,
            headers={HEADERS_TOTAL_COUNT: 1},
            events=[
                RESPONSE,
            ],
        )

        count = self.arch.events.count(
            asset_id=ASSET_ID,
            props={'confirmation_status': 'CONFIRMED', },
        )
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                        "?page_size=1"
                        "&confirmation_status=CONFIRMED"
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
    def test_events_count_with_attrs_query(self, mock_get):
        '''
        Test event counting
        '''
        mock_get.return_value = MockResponse(
            200,
            headers={HEADERS_TOTAL_COUNT: 1},
            events=[
                RESPONSE,
            ],
        )

        count = self.arch.events.count(
            asset_id=ASSET_ID,
            attrs={"arc_firmware_version": "1.0"},
        )
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                        "?page_size=1"
                        "&event_attributes.arc_firmware_version=1.0"
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
    def test_events_count_with_wildcard_asset(self, mock_get):
        '''
        Test event counting
        '''
        mock_get.return_value = MockResponse(
            200,
            headers={HEADERS_TOTAL_COUNT: 1},
            events=[
                RESPONSE,
            ],
        )

        count = self.arch.events.count(
            attrs={"arc_firmware_version": "1.0"},
        )
        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_WILDCARD}"
                        f"/{EVENTS_LABEL}"
                        "?page_size=1"
                        "&event_attributes.arc_firmware_version=1.0"
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
    def test_events_list(self, mock_get):
        '''
        Test event listing
        '''
        mock_get.return_value = MockResponse(
            200,
            events=[
                RESPONSE,
            ],
        )

        listing = self.arch.events.list(asset_id=ASSET_ID)
        events = [a for a in listing]
        self.assertEqual(
            len(events),
            1,
            msg="incorrect number of events",
        )
        for event in events:
            self.assertEqual(
                event,
                RESPONSE,
                msg="Incorrect event listed",
            )

        for a in mock_get.call_args_list:
            self.assertEqual(
                tuple(a),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                            f"?page_size={DEFAULT_PAGE_SIZE}"
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
    def test_events_list_with_query(self, mock_get):
        '''
        Test event listing
        '''
        mock_get.return_value = MockResponse(
            200,
            events=[
                RESPONSE,
            ],
        )

        listing = self.arch.events.list(
            asset_id=ASSET_ID,
            props={'confirmation_status': 'CONFIRMED', },
            attrs={"arc_firmware_version": "1.0"},
        )
        events = [a for a in listing]
        self.assertEqual(
            len(events),
            1,
            msg="incorrect number of events",
        )
        for event in events:
            self.assertEqual(
                event,
                RESPONSE,
                msg="Incorrect event listed",
            )

        for a in mock_get.call_args_list:
            self.assertEqual(
                tuple(a),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                            f"/{EVENTS_LABEL}"
                            f"?page_size={DEFAULT_PAGE_SIZE}"
                            "&confirmation_status=CONFIRMED"
                            "&event_attributes.arc_firmware_version=1.0"
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
    def test_events_list_with_wildcard_asset(self, mock_get):
        '''
        Test event listing
        '''
        mock_get.return_value = MockResponse(
            200,
            events=[
                RESPONSE,
            ],
        )

        listing = self.arch.events.list(
            props={'confirmation_status': 'CONFIRMED', },
            attrs={"arc_firmware_version": "1.0"},
        )
        events = [a for a in listing]
        self.assertEqual(
            len(events),
            1,
            msg="incorrect number of events",
        )
        for event in events:
            self.assertEqual(
                event,
                RESPONSE,
                msg="Incorrect event listed",
            )

        for a in mock_get.call_args_list:
            self.assertEqual(
                tuple(a),
                (
                    (
                        (
                            f"url/{ROOT}/{ASSETS_SUBPATH}"
                            f"/{ASSETS_WILDCARD}"
                            f"/{EVENTS_LABEL}"
                            f"?page_size={DEFAULT_PAGE_SIZE}"
                            "&confirmation_status=CONFIRMED"
                            "&event_attributes.arc_firmware_version=1.0"
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
    def test_events_read_by_signature(self, mock_get):
        '''
        Test event listing
        '''
        mock_get.return_value = MockResponse(
            200,
            events=[
                RESPONSE,
            ],
        )

        event = self.arch.events.read_by_signature(asset_id=ASSET_ID)
        self.assertEqual(
            event,
            RESPONSE,
            msg="Incorrect event listed",
        )

        self.assertEqual(
            tuple(mock_get.call_args),
            (
                (
                    (
                        f"url/{ROOT}/{ASSETS_SUBPATH}"
                        f"/{ASSETS_LABEL}/xxxxxxxxxxxxxxxxxxxx"
                        f"/{EVENTS_LABEL}"
                        f"?page_size=2"
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
