from __future__ import annotations

from typing import Literal, TypedDict

from .common import PaginationParams, WebhookEventType
from .webhook import WebhookEvent


class EventQueue(TypedDict):
    object: Literal["event_queue"]
    id: str
    events: list[WebhookEventType]
    description: str | None
    mailbox_ids: list[str] | None
    domain_ids: list[str] | None
    include_reply_text: bool
    authenticated_senders_only: bool
    allowed_senders: list[str] | None
    created_at: str


class _CreateEventQueueParamsRequired(TypedDict):
    events: list[WebhookEventType]


class CreateEventQueueParams(_CreateEventQueueParamsRequired, total=False):
    description: str
    mailbox_ids: list[str] | None
    domain_ids: list[str] | None
    include_reply_text: bool
    authenticated_senders_only: bool
    allowed_senders: list[str] | None


ListEventQueuesParams = PaginationParams


class ListEventQueueEventsParams(TypedDict, total=False):
    limit: int


class EventQueueEvents(TypedDict):
    """The oldest unacknowledged events, each exactly the envelope a webhook delivery carries."""

    data: list[WebhookEvent]
    has_more: bool


class AckEventQueueEventsResponse(TypedDict):
    acknowledged: int
