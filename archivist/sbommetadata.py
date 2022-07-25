"""SBOMS Metadata dataclass

"""

# pylint:disable=too-few-public-methods
# pylint:disable=too-many-instance-attributes

from __future__ import annotations
from dataclasses import dataclass, asdict
from inspect import signature as inspect_signature
from logging import getLogger

# NB: the order of the fields is important. Fields with default values must
#    appear after fields without.

LOGGER = getLogger(__name__)


@dataclass(frozen=True)
class SBOM:
    """
    SBOM definition
    """

    identity: str
    authors: list[str]
    supplier: str
    component: str
    version: str
    hashes: list[str]
    unique_id: str
    upload_date: str
    uploaded_by: str
    trusted: bool
    lifecycle_status: str
    withdrawn_date: str
    published_date: str
    rkvst_link: str = ""
    tenantid: str = ""

    def dict(self):
        """Emit dictionary representation"""
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, indict):
        """Ignore unexpected fields"""
        params = inspect_signature(cls).parameters
        diff = set(indict) - set(params)
        if diff:
            LOGGER.info("WARN: extra keys %s ignored", diff)
        return cls(**{k: indict[k] for k in params})
