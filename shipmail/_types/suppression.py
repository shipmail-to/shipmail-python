from __future__ import annotations

from typing import Literal, Optional, TypedDict

from .common import PaginationParams

SuppressionReason = Literal["hard_bounce", "complaint", "manual", "soft_bounce"]
# "all" blocks every send. The others come from a complaint and block one kind of email:
# "marketing" newsletters, "transactional" application senders, "mailbox" mail from a mailbox.
SuppressionScope = Literal["all", "marketing", "transactional", "mailbox"]
# The scopes an entry you add can have.
CreateSuppressionScope = Literal["all", "marketing"]


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
    scope: CreateSuppressionScope
