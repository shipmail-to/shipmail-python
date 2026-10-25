from __future__ import annotations

from typing import Literal, TypedDict

from .newsletter import NewsletterBlock, NewsletterStylingMode


class WelcomeStep(TypedDict):
    object: Literal["welcome_step"]
    id: str
    audience_id: str | None
    position: int
    wait_minutes: int
    sender_identity_id: str | None
    subject: str | None
    preview_text: str | None
    blocks: list[NewsletterBlock]
    track_engagement: bool
    add_utm_tags: bool
    styling_mode: NewsletterStylingMode
    sent_count: int
    delivered_count: int
    bounced_count: int
    complained_count: int
    created_at: str
    updated_at: str


class WelcomeSequence(TypedDict):
    object: Literal["welcome_sequence"]
    audience_id: str
    enabled: bool
    paused: bool
    pause_reason: str | None
    active_readers: int
    completed_readers: int
    steps: list[WelcomeStep]


class UpdateWelcomeSequenceParams(TypedDict):
    enabled: bool


class _CreateWelcomeStepRequired(TypedDict):
    subject: str


class CreateWelcomeStepParams(_CreateWelcomeStepRequired, total=False):
    preview_text: str | None
    blocks: list[NewsletterBlock]
    content_markdown: str
    wait_minutes: int
    sender_identity_id: str
    track_engagement: bool
    add_utm_tags: bool
    styling_mode: NewsletterStylingMode


class UpdateWelcomeStepParams(TypedDict, total=False):
    subject: str
    preview_text: str | None
    blocks: list[NewsletterBlock]
    content_markdown: str
    wait_minutes: int
    sender_identity_id: str
    track_engagement: bool
    add_utm_tags: bool
    styling_mode: NewsletterStylingMode


class DeletedWelcomeStep(TypedDict):
    object: Literal["welcome_step"]
    id: str
    deleted: Literal[True]
