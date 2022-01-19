"""SBOMS Metadata dataclass

"""

# pylint:disable=too-few-public-methods
# pylint:disable=too-many-instance-attributes

from dataclasses import dataclass, asdict
import logging
from typing import List

# NB: the order of the fields is important. Fields with default values must
#    appear after fields without.

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SBOM:
    """
    SBOM definition
    """

    identity: str
    authors: List[str]
    supplier: str
    component: str
    version: str
    hashes: List[str]
    unique_id: str
    upload_date: str
    uploaded_by: str
    trusted: bool
    lifecycle_status: str
    withdrawn_date: str
    published_date: str
    rkvst_link: str = ""

    def dict(self):
        """Emit dictionary representation"""
        d = asdict(self)
        return d
