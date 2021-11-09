"""Archivist Compliance Policy Type

   Enumerated type that allows user to select the compliance policy type when
   creating a compliance policy.

"""

from enum import Enum


class CompliancePolicyType(Enum):
    """
    Enumerate types of compliance policy
    """

    COMPLIANCE_TYPE_UNDEFINED = 0
    #: Time since specific event for specified period
    COMPLIANCE_SINCE = 1
    #: Unresolved event currently on asset (eg. vulnerability)
    COMPLIANCE_CURRENT_OUTSTANDING = 2
    #: No unresolved events for longer than specified period
    COMPLIANCE_PERIOD_OUTSTANDING = 3
    #: dynamic tolerance with dynamic window etc..
    COMPLIANCE_DYNAMIC_TOLERANCE = 4
    #: Compliance on comparison of asset attribute value to predefined comparator
    COMPLIANCE_RICHNESS = 5
