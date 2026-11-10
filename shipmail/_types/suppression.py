from __future__ import annotations

from typing import Literal, Optional, TypedDict, Union

from .common import PaginationParams

SuppressionReason = Literal["hard_bounce", "complaint", "manual", "soft_bounce"]
# The reasons the list shows: a suppression's own, or "unsubscribe" for a newsletter opt-out.
SuppressionEntryReason = Literal["hard_bounce", "complaint", "manual", "soft_bounce", "unsubscribe"]
# "suppression" is address health (bounces, complaints, manual blocks), which remove() lifts.
# "newsletter_optout" is the reader's own unsubscribe, which only a resubscribe lifts.
SuppressionSource = Literal["suppression", "newsletter_optout"]
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
    source: Literal["suppression"]


class NewsletterOptoutSuppression(TypedDict):
    """A newsletter opt-out as the suppression list shows it. It blocks newsletters only."""

    object: Literal["suppression"]
    email_address: str
    reason: Literal["unsubscribe"]
    scope: Literal["marketing"]
    expires_at: None
    created_at: str
    source: Literal["newsletter_optout"]
    # The issue the reader unsubscribed from, when known.
    newsletter_id: Optional[str]
    # True when the opt-out came from a test send.
    test_send: bool


# One item of suppressions.list(): tell them apart by "source".
SuppressionEntry = Union[Suppression, NewsletterOptoutSuppression]


class SuppressionRemoval(TypedDict):
    """remove() removed the suppression, but the address keeps its newsletter opt-out."""

    object: Literal["suppression_removal"]
    email_address: str
    removed: Literal[True]
    newsletter_optout_remains: Literal[True]
    message: str


class ResubscribeNewsletterOptoutParams(TypedDict):
    # Where and how the reader opted in again.
    consent_source: str


class NewsletterOptoutLift(TypedDict):
    """resubscribe() lifted the address's newsletter opt-out with fresh consent."""

    object: Literal["newsletter_opt_out_lift"]
    email_address: str
    consent_source: str
    consent_attested_at: str
    # When the lifted opt-out was recorded.
    opted_out_at: str
    # The newsletter the reader had unsubscribed from, when known.
    newsletter_id: Optional[str]


class ListSuppressionsParams(PaginationParams, total=False):
    scope: SuppressionScope
    reason: SuppressionEntryReason


class _CreateSuppressionParamsRequired(TypedDict):
    email: str


class CreateSuppressionParams(_CreateSuppressionParamsRequired, total=False):
    # Defaults to "all".
    scope: CreateSuppressionScope
