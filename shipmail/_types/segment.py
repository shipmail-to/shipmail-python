from __future__ import annotations

from typing import Literal, TypedDict, Union

SegmentEngagementTier = Literal["engaged", "cooling", "cold", "dormant", "not_enough_data"]


class SegmentMergeFieldValueRule(TypedDict):
    """A merge field compared case-insensitively with a value."""

    kind: Literal["merge_field"]
    field: str
    operator: Literal["equals", "not_equals", "contains", "not_contains"]
    value: str


class _SegmentMergeFieldPresenceRuleRequired(TypedDict):
    kind: Literal["merge_field"]
    field: str
    operator: Literal["is_set", "is_not_set"]


class SegmentMergeFieldPresenceRule(_SegmentMergeFieldPresenceRuleRequired, total=False):
    """Whether a merge field has a value. Takes no value."""

    value: Literal[""]


SegmentMergeFieldRule = Union[SegmentMergeFieldValueRule, SegmentMergeFieldPresenceRule]


class SegmentJoinDateRule(TypedDict):
    """The day the subscriber joined, compared in UTC. ``value`` is a YYYY-MM-DD date."""

    kind: Literal["join_date"]
    operator: Literal["before", "after", "on_or_before", "on_or_after"]
    value: str


class SegmentEngagementTierRule(TypedDict):
    kind: Literal["engagement_tier"]
    operator: Literal["is", "is_not"]
    value: SegmentEngagementTier


class SegmentLastSignOfLifeRule(TypedDict):
    """An open or click in the last ``value`` days (1 to 3650), or none in them."""

    kind: Literal["last_sign_of_life"]
    operator: Literal["within_days", "not_within_days"]
    value: int


class SegmentIssuesReceivedRule(TypedDict):
    """How many newsletters the subscriber has received, from 0 to 100000."""

    kind: Literal["issues_received"]
    operator: Literal["at_least", "at_most"]
    value: int


SegmentRule = Union[
    SegmentMergeFieldValueRule,
    SegmentMergeFieldPresenceRule,
    SegmentJoinDateRule,
    SegmentEngagementTierRule,
    SegmentLastSignOfLifeRule,
    SegmentIssuesReceivedRule,
]


class SegmentDefinition(TypedDict):
    """``all`` requires every rule to match, ``any`` at least one. From 1 to 10 rules."""

    match: Literal["all", "any"]
    rules: list[SegmentRule]


class Segment(TypedDict):
    """A saved group of an audience's subscribers. Use its id as ``segment_id``."""

    object: Literal["segment"]
    id: str
    audience_id: str
    name: str
    definition: SegmentDefinition
    matching_count: int
    created_at: str
    updated_at: str


class ListSegmentsResponse(TypedDict):
    data: list[Segment]


class CreateSegmentParams(TypedDict):
    name: str
    definition: SegmentDefinition


class UpdateSegmentParams(TypedDict, total=False):
    """Pass name, definition, or both."""

    name: str
    definition: SegmentDefinition
