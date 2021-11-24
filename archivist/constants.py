"""Archivist constants

"""

# these are in separate file to stop import loops
ROOT = "archivist"
SEP = "/"
VERBSEP = ":"

# define in MIME canonical form
HEADERS_REQUEST_TOTAL_COUNT = "X-Request-Total-Count"
HEADERS_TOTAL_COUNT = "X-Total-Count"
HEADERS_RETRY_AFTER = "Archivist-Rate-Limit-Reset"

CONFIRMATION_STATUS = "confirmation_status"
CONFIRMATION_PENDING = "PENDING"
CONFIRMATION_FAILED = "FAILED"
CONFIRMATION_CONFIRMED = "CONFIRMED"

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

ATTACHMENTS_SUBPATH = "v1"
ATTACHMENTS_LABEL = "blobs"

ACCESS_POLICIES_SUBPATH = "iam/v1"
ACCESS_POLICIES_LABEL = "access_policies"

COMPLIANCE_SUBPATH = "v1"
COMPLIANCE_LABEL = "compliance"

COMPLIANCE_POLICIES_SUBPATH = "v1"
COMPLIANCE_POLICIES_LABEL = "compliance_policies"

LOCATIONS_SUBPATH = "v2"
LOCATIONS_LABEL = "locations"

SBOMS_SUBPATH = "v1"
SBOMS_LABEL = "sboms"
SBOMS_WILDCARD = "-/metadata"
SBOMS_METADATA = "metadata"
SBOMS_PUBLISH = "publish"
SBOMS_WITHDRAW = "withdraw"

SUBJECTS_SUBPATH = "iam/v1"
SUBJECTS_LABEL = "subjects"
