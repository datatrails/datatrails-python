"""Archivist constants

"""

# these are in separate file to stop import loops
ROOT = "archivist"
SEP = "/"
VERBSEP = ":"

# These are now hardcoded and not user-selectable. Eventually they will be removed from
# the backend API and removed from this package.
ASSET_BEHAVIOURS = [
    "RecordEvidence",
]

USER_AGENT = "DataTrails-User-Agent"
USER_AGENT_PREFIX = "pysdk/"
PARTNER_ID = "DataTrails-Partner-ID"

# bearer token
AUTHORIZATION_KEY = "authorization"
BEARER_PREFIX = "Bearer"

BINARY_CONTENT = "application/octet-stream"

# define in MIME canonical form
HEADERS_REQUEST_TOTAL_COUNT = "X-Request-Total-Count"
HEADERS_TOTAL_COUNT = "X-Total-Count"
HEADERS_RETRY_AFTER = "Archivist-Rate-Limit-Reset"

PROOF_MECHANISM = "proof_mechanism"

CONFIRMATION_STATUS = "confirmation_status"

APPIDP_SUBPATH = "iam/v1"
APPIDP_LABEL = "appidp"
APPIDP_TOKEN = "token"

APPLICATIONS_SUBPATH = "iam/v1"
APPLICATIONS_LABEL = "applications"
APPLICATIONS_REGENERATE = "regenerate-secret"

ASSETS_SUBPATH = "v2"
ASSETS_LABEL = "assets"
ASSETS_WILDCARD = "assets/-"
EVENTS_LABEL = "events"

PUBLICASSETS_LABEL = "publicassets"

ATTACHMENTS_SUBPATH = "v1"
ATTACHMENTS_LABEL = "blobs"

ASSETATTACHMENTS_SUBPATH = "v2"
ASSETATTACHMENTS_LABEL = "attachments"

ACCESS_POLICIES_SUBPATH = "iam/v1"
ACCESS_POLICIES_LABEL = "access_policies"

SBOM_PACKAGE = "Software Package"
SBOM_RELEASE = "Software Package Release"

SUBJECTS_SUBPATH = "iam/v1"
SUBJECTS_LABEL = "subjects"
SUBJECTS_SELF_ID = "subjects/00000000-0000-0000-0000-000000000000"

TENANCIES_SUBPATH = "v1"
TENANCIES_LABEL = "tenancies"

# values of tenant identity in response from other endpoints is 'tenant'
# and not 'tenancies'.
TENANCIES_PREFIX = "tenant"
