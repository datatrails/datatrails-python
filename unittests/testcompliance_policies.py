"""
Test compliance policies
"""

from unittest import TestCase, mock

from archivist.archivist import Archivist
from archivist.compliance_policies import (
    CompliancePolicy,
)
from archivist.compliance_policy_requests import (
    CompliancePolicySince,
)
from archivist.constants import (
    COMPLIANCE_POLICIES_LABEL,
    COMPLIANCE_POLICIES_SUBPATH,
    HEADERS_REQUEST_TOTAL_COUNT,
    HEADERS_TOTAL_COUNT,
    ROOT,
)
from archivist.errors import ArchivistBadRequestError

from .mock_response import MockResponse

# pylint: disable=missing-docstring
# pylint: disable=protected-access
# pylint: disable=unused-variable

SINCE_POLICY = CompliancePolicySince(
    description="since description",
    display_name="since display_name",
    asset_filter=[
        ["a", "b"],
        ["x", "z"],
    ],
    event_display_type="since event_display_type",
    time_period_seconds=10,
)
SINCE_POLICY_REQUEST = SINCE_POLICY.dict()

IDENTITY = f"{COMPLIANCE_POLICIES_LABEL}/xxxxxxxx"
SUBPATH = f"{COMPLIANCE_POLICIES_SUBPATH}/{COMPLIANCE_POLICIES_LABEL}"

SINCE_RESPONSE = {
    **SINCE_POLICY_REQUEST,
    "identity": IDENTITY,
    "compliance_type": "SINCE",
}
SINCE_REQUEST = {
    **SINCE_POLICY_REQUEST,
}


class TestCompliancePolicy(TestCase):
    """
    Test Archivist CompliancePolicy
    """

    maxDiff = None

    def test_compliance_policy(self):
        """
        Test compliance_policy
        """
        self.assertEqual(
            CompliancePolicy(**SINCE_RESPONSE).name,
            "since display_name",
            msg="Incorrct name property",
        )

    def test_compliance_policy_without_name(self):
        """
        Test compliance_policy
        """
        self.assertIsNone(
            CompliancePolicy(**{"description": "descriptton"}).name,
            msg="Incorrct name property",
        )


class TestCompliancePolicies(TestCase):
    """
    Test Archivist CompliancePolicies Create method
    """

    maxDiff = None

    def setUp(self):
        self.arch = Archivist("url", "authauthauth")

    def tearDown(self):
        self.arch.close()

    def test_compliance_policies_str(self):
        """
        Test compliance_policy str
        """
        self.assertEqual(
            str(self.arch.compliance_policies),
            "CompliancePoliciesClient(url)",
            msg="Incorrect str",
        )

    def test_compliance_policies_create(self):
        """
        Test compliance_policy creation
        """
        with mock.patch.object(self.arch.session, "post") as mock_post:
            mock_post.return_value = MockResponse(200, **SINCE_RESPONSE)

            compliance_policy = self.arch.compliance_policies.create(
                SINCE_POLICY,
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
                    "json": SINCE_REQUEST,
                    "headers": {
                        "authorization": "Bearer authauthauth",
                    },
                },
                msg="CREATE method kwargs called incorrectly",
            )
            self.assertEqual(
                compliance_policy,
                SINCE_RESPONSE,
                msg="CREATE method called incorrectly",
            )

    def test_compliance_policies_read(self):
        """
        Test compliance_policy reading
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(200, **SINCE_RESPONSE)

            self.arch.compliance_policies.read(IDENTITY)
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{COMPLIANCE_POLICIES_SUBPATH}/{IDENTITY}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                        "params": None,
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_compliance_policies_delete(self):
        """
        Test compliance_policy deleting
        """
        with mock.patch.object(self.arch.session, "delete") as mock_delete:
            mock_delete.return_value = MockResponse(200, {})

            self.arch.compliance_policies.delete(IDENTITY)
            self.assertEqual(
                tuple(mock_delete.call_args),
                (
                    ((f"url/{ROOT}/{COMPLIANCE_POLICIES_SUBPATH}/{IDENTITY}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                    },
                ),
                msg="DELETE method called incorrectly",
            )

    def test_compliance_policies_read_with_error(self):
        """
        Test read method with error
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(400)
            with self.assertRaises(ArchivistBadRequestError):
                self.arch.compliance_policies.read(IDENTITY)

    def test_compliance_policies_count(self):
        """
        Test compliance_policy counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                compliance_policies=[
                    SINCE_RESPONSE,
                ],
            )

            count = self.arch.compliance_policies.count()
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
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

    def test_compliance_policies_count_by_name(self):
        """
        Test compliance_policy counting
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                headers={HEADERS_TOTAL_COUNT: 1},
                compliance_policies=[
                    SINCE_RESPONSE,
                ],
            )

            self.arch.compliance_policies.count(
                props={"compliance_type": "SINCE"},
            )
            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    ((f"url/{ROOT}/{SUBPATH}"),),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                            HEADERS_REQUEST_TOTAL_COUNT: "true",
                        },
                        "params": {"page_size": 1, "compliance_type": "SINCE"},
                    },
                ),
                msg="GET method called incorrectly",
            )

    def test_compliance_policies_list(self):
        """
        Test compliance_policy listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                compliance_policies=[
                    SINCE_RESPONSE,
                ],
            )

            compliance_policies = list(self.arch.compliance_policies.list())
            self.assertEqual(
                len(compliance_policies),
                1,
                msg="incorrect number of compliance_policies",
            )
            for compliance_policy in compliance_policies:
                self.assertEqual(
                    compliance_policy,
                    SINCE_RESPONSE,
                    msg="Incorrect compliance_policy listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        (f"url/{ROOT}/{SUBPATH}",),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {},
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_compliance_policies_list_by_name(self):
        """
        Test compliance_policy listing
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                compliance_policies=[
                    SINCE_RESPONSE,
                ],
            )

            compliance_policies = list(
                self.arch.compliance_policies.list(
                    props={"compliance_type": "SINCE"},
                )
            )
            self.assertEqual(
                len(compliance_policies),
                1,
                msg="incorrect number of compliance_policies",
            )
            for compliance_policy in compliance_policies:
                self.assertEqual(
                    compliance_policy,
                    SINCE_RESPONSE,
                    msg="Incorrect compliance_policy listed",
                )

            for a in mock_get.call_args_list:
                self.assertEqual(
                    tuple(a),
                    (
                        ((f"url/{ROOT}/{SUBPATH}"),),
                        {
                            "headers": {
                                "authorization": "Bearer authauthauth",
                            },
                            "params": {"compliance_type": "SINCE"},
                        },
                    ),
                    msg="GET method called incorrectly",
                )

    def test_compliance_policies_read_by_signature(self):
        """
        Test compliance policies read_by_signature
        """
        with mock.patch.object(self.arch.session, "get") as mock_get:
            mock_get.return_value = MockResponse(
                200,
                compliance_policies=[
                    SINCE_RESPONSE,
                ],
            )

            policy = self.arch.compliance_policies.read_by_signature()
            self.assertEqual(
                policy,
                SINCE_RESPONSE,
                msg="Incorrect compliance_policy listed",
            )

            self.assertEqual(
                tuple(mock_get.call_args),
                (
                    (f"url/{ROOT}/{SUBPATH}",),
                    {
                        "headers": {
                            "authorization": "Bearer authauthauth",
                        },
                        "params": {"page_size": 2},
                    },
                ),
                msg="GET method called incorrectly",
            )
