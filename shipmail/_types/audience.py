from __future__ import annotations

from typing import Literal, TypedDict, Union

from .common import PaginationParams
from .suppression import SuppressionReason

SubscriberStatus = Literal[
    "subscribed",
    "pending",
    "unsubscribed",
    "bounced",
    "complained",
    "suppressed",
    "transactional_only",
    "dormant",
]
SubscriberOutcome = Literal[
    "created",
    "updated",
    "skipped_not_mailable",
    "skipped_invalid",
    "skipped_cap",
    "skipped_quota",
]

# Why an add skipped an address as not mailable. "not_resubscribable_status" means the member is
# unsubscribed, bounced or complained in this audience; only resubscribe changes that.
SubscriberSkipReason = Literal[
    "unsubscribed",
    "complaint",
    "hard_bounce",
    "soft_bounce",
    "manual",
    "not_resubscribable_status",
]

MergeFields = dict[str, str | int | float | bool | None]


class EmailCopyEntry(TypedDict):
    """One language's wording: a one-line subject (at most 120 characters) and a plain-text
    message (at most 600)."""

    subject: str
    message: str


class EmailCopy(TypedDict, total=False):
    """An audience's own wording for one of its emails, per language. Only the subject and the
    opening message change; the button, links, expiry, unsubscribe link and sender details stay
    fixed. A language left out, and a reader whose email is in another language, get the built-in
    email. Text may hold no links or domain names, email addresses, phone numbers or invisible
    characters."""

    en: EmailCopyEntry
    fr: EmailCopyEntry
    es: EmailCopyEntry


class Audience(TypedDict):
    object: Literal["audience"]
    id: str
    name: str
    description: str | None
    member_count: int
    subscribed_count: int
    consent_source: str | None
    feed_enabled: bool
    feed_url: str | None
    # Whether new issues for this audience start with a View in browser link.
    view_in_browser_default: bool
    cleanup_enabled: bool
    cleanup_ignored_issues: int
    cleanup_inactive_days: int
    confirmation_email_copy: EmailCopy | None
    last_chance_email_copy: EmailCopy | None
    created_at: str
    updated_at: str


class AudienceFeed(TypedDict):
    object: Literal["audience_feed"]
    audience_id: str
    enabled: bool
    title: str | None
    subtitle: str | None
    site_url: str | None
    canonical_url: str | None
    author_name: str | None
    icon_url: str | None
    entry_limit: int | None
    url: str | None
    updated_at: str


class OptoutNotMailableReason(TypedDict):
    """The reader unsubscribed from the organization's newsletters. Only a resubscribe lifts it."""

    reason: Literal["unsubscribed"]
    source: Literal["newsletter_optout"]
    created_at: str
    # The issue the reader unsubscribed from, when known.
    newsletter_id: str | None
    # True when the opt-out came from a test send.
    test_send: bool


class SuppressionNotMailableReason(TypedDict):
    """An address-health suppression (bounce, complaint or manual block)."""

    reason: SuppressionReason
    source: Literal["suppression"]
    created_at: str
    # None when the suppression is permanent.
    expires_at: str | None


# Tell them apart by "source".
NotMailableReason = Union[OptoutNotMailableReason, SuppressionNotMailableReason]


class Subscriber(TypedDict):
    object: Literal["subscriber"]
    id: str
    audience_id: str
    email_address: str
    display_name: str | None
    # Per audience.
    status: SubscriberStatus
    # Whether the organization may send newsletters to the address now. False when an
    # organization-wide opt-out or suppression blocks it, whatever the status in this audience.
    mailable: bool
    # What blocks the address, most decisive first. Empty when mailable.
    not_mailable_reasons: list[NotMailableReason]
    merge_fields: MergeFields
    consent_source: str | None
    created_at: str
    updated_at: str


class _CreateAudienceParamsRequired(TypedDict):
    name: str
    consent_source: str


class CreateAudienceParams(_CreateAudienceParamsRequired, total=False):
    description: str | None


class UpdateAudienceParams(TypedDict, total=False):
    name: str
    description: str | None
    view_in_browser_default: bool
    cleanup_enabled: bool
    cleanup_ignored_issues: int
    cleanup_inactive_days: int
    # Replaces that email's wording; None or {} clears it. Adding or changing text needs a paid
    # plan and newsletter sending in good standing (403 otherwise).
    confirmation_email_copy: EmailCopy | None
    last_chance_email_copy: EmailCopy | None


class UpdateAudienceFeedParams(TypedDict, total=False):
    enabled: bool
    title: str | None
    subtitle: str | None
    site_url: str | None
    canonical_url: str | None
    author_name: str | None
    icon_url: str | None
    entry_limit: int | None


ListAudiencesParams = PaginationParams


class _AddSubscriberParamsRequired(TypedDict):
    email_address: str


class AddSubscriberParams(_AddSubscriberParamsRequired, total=False):
    display_name: str | None
    merge_fields: MergeFields
    consent_source: str | None
    consent_ip: str | None


class AddSubscribersBatchParams(TypedDict):
    subscribers: list[AddSubscriberParams]


class UpdateSubscriberParams(TypedDict, total=False):
    display_name: str | None
    merge_fields: MergeFields


class ResubscribeSubscriberParams(TypedDict):
    consent_source: str


class ResendSubscriberConfirmationParams(TypedDict, total=False):
    subscriber_ids: list[str]


class ConfirmationResendSkipped(TypedDict):
    not_found: int
    not_pending: int
    too_old: int
    resend_limit: int
    recently_sent: int


class ConfirmationResend(TypedDict):
    object: Literal["confirmation_resend"]
    audience_id: str
    sent: int
    failed: int
    skipped: ConfirmationResendSkipped
    remaining: int


class _SubscriberResultRequired(TypedDict):
    email_address: str
    outcome: SubscriberOutcome


class SubscriberResult(_SubscriberResultRequired, total=False):
    # Present only when outcome is "skipped_not_mailable".
    reason: SubscriberSkipReason


class AddSubscribersBatchResult(TypedDict):
    results: list[SubscriberResult]


class ListSubscribersParams(PaginationParams, total=False):
    status: SubscriberStatus
    email: str
