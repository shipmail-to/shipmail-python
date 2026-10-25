from __future__ import annotations

from typing import Literal, TypedDict

from .common import PaginationParams

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

MergeFields = dict[str, str | int | float | bool | None]


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
    cleanup_enabled: bool
    cleanup_ignored_issues: int
    cleanup_inactive_days: int
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


class Subscriber(TypedDict):
    object: Literal["subscriber"]
    id: str
    audience_id: str
    email_address: str
    display_name: str | None
    status: SubscriberStatus
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
    cleanup_enabled: bool
    cleanup_ignored_issues: int
    cleanup_inactive_days: int


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


class SubscriberResult(TypedDict):
    email_address: str
    outcome: SubscriberOutcome


class AddSubscribersBatchResult(TypedDict):
    results: list[SubscriberResult]


class ListSubscribersParams(PaginationParams, total=False):
    status: SubscriberStatus
    email: str
