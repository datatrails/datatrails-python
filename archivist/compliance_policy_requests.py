"""Archivist Compliance Policy Requests

   Dataclasses that represent the different types of compliance policies

"""

from dataclasses import dataclass, asdict
from typing import List

from .compliance_policy_type import CompliancePolicyType
from .or_dict import and_list

# NB: the oder of the fields is important. Fields with default values must
#    appear after fields without. This is why the compliance_type is last
#    in every case.


@dataclass(frozen=True)
class CompliancePolicyBase:
    """
    Compliance policy base definition
    """

    description: str
    display_name: str
    asset_filter: List[List]

    def dict(self):
        """Emit dictionary representation"""
        d = asdict(self)
        d["asset_filter"] = and_list(d["asset_filter"])
        return d


@dataclass(frozen=True)
class CompliancePolicySince(CompliancePolicyBase):
    """
    Compliance policy that indicates if an event has 'expired'
    """

    event_display_type: str
    time_period_seconds: int
    compliance_type: str = CompliancePolicyType.COMPLIANCE_SINCE.name


@dataclass(frozen=True)
class CompliancePolicyCurrentOutstanding(CompliancePolicyBase):
    """
    Compliance policy that indicates if an event has been 'closed'
    """

    event_display_type: str
    compliance_type: str = CompliancePolicyType.COMPLIANCE_CURRENT_OUTSTANDING.name


@dataclass(frozen=True)
class CompliancePolicyPeriodOutstanding(CompliancePolicyBase):
    """
    Compliance policy that indicates if an event has been 'closed' within
    a specified time
    """

    event_display_type: str
    closing_event_display_type: str
    time_period_seconds: int
    compliance_type: str = CompliancePolicyType.COMPLIANCE_PERIOD_OUTSTANDING.name


@dataclass(frozen=True)
class CompliancePolicyDynamicTolerance(CompliancePolicyBase):
    """
    Compliance policy that indicates if the average time between opening
    and closing events in a specified period of time does not exceed a
    specified number of standard deviations from the mean.
    """

    event_display_type: str
    closing_event_display_type: str
    dynamic_window: int
    dynamic_variability: float
    compliance_type: str = CompliancePolicyType.COMPLIANCE_DYNAMIC_TOLERANCE.name


@dataclass(frozen=True)
class CompliancePolicyRichness(CompliancePolicyBase):
    """
    Compliance policy that indicates if an asset has an attribute that
    complies with a set of assertions.
    """

    richness_assertions: List[List]
    compliance_type: str = CompliancePolicyType.COMPLIANCE_RICHNESS.name

    def dict(self):
        """Emit dictionary representation"""
        d = asdict(self)
        d["asset_filter"] = and_list(d["asset_filter"])
        d["richness_assertions"] = and_list(d["richness_assertions"])
        return d
