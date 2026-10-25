from __future__ import annotations

from typing import Literal, Optional, TypedDict

from .common import PaginationParams

SuppressionReason = Literal["hard_bounce", "complaint", "manual", "soft_bounce"]
# "all" blocks every send. "marketing" blocks newsletter sends only.
SuppressionScope = Literal["all", "marketing"]


class Suppression(TypedDict):
    object: Literal["suppression"]
    email_address: str
    reason: SuppressionReason
    scope: SuppressionScope
    # None when the entry is permanent.
    expires_at: Optional[str]
    created_at: str


class ListSuppressionsParams(PaginationParams, total=False):
    scope: SuppressionScope


class _CreateSuppressionParamsRequired(TypedDict):
    email: str


class CreateSuppressionParams(_CreateSuppressionParamsRequired, total=False):
    # Defaults to "all".
    scope: SuppressionScope
