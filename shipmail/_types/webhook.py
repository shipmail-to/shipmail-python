from __future__ import annotations

from typing import Any, Literal, TypedDict

from .common import (
    DataMode,
    PaginationParams,
    WebhookDeliveryEventType,
    WebhookDeliveryStatus,
    WebhookEventType,
)


class Webhook(TypedDict):
    object: Literal["webhook"]
    id: str
    url: str
    events: list[WebhookEventType]
    active: bool
    description: str | None
    mailbox_ids: list[str] | None
    domain_ids: list[str] | None
    has_authorization: bool
    has_standard_webhooks_secret: bool
    include_reply_text: bool
    authenticated_senders_only: bool
    allowed_senders: list[str] | None
    created_at: str
    updated_at: str


class WebhookWithSecret(Webhook):
    secret: str


class _CreateWebhookParamsRequired(TypedDict):
    url: str
    events: list[WebhookEventType]


class CreateWebhookParams(_CreateWebhookParamsRequired, total=False):
    description: str
    mailbox_ids: list[str] | None
    domain_ids: list[str] | None
    authorization: str | None
    standard_webhooks_secret: str | None
    include_reply_text: bool
    authenticated_senders_only: bool
    allowed_senders: list[str] | None


class UpdateWebhookParams(TypedDict, total=False):
    url: str
    events: list[WebhookEventType]
    description: str | None
    active: bool
    mailbox_ids: list[str] | None
    domain_ids: list[str] | None
    authorization: str | None
    standard_webhooks_secret: str | None
    include_reply_text: bool
    authenticated_senders_only: bool
    allowed_senders: list[str] | None


ListWebhooksParams = PaginationParams


class RotateSecretResponse(TypedDict):
    secret: str
    previous_secret_expires_at: str


class TestWebhookResponse(TypedDict):
    event_id: str


class WebhookDelivery(TypedDict):
    object: Literal["webhook_delivery"]
    id: str
    event_id: str
    event_type: WebhookDeliveryEventType
    mode: DataMode
    status: WebhookDeliveryStatus
    attempts: int
    last_status_code: int | None
    last_error: str | None
    created_at: str
    delivered_at: str | None


class WebhookDeliveryDetail(WebhookDelivery):
    payload: Any
    next_attempt_at: str | None
    replayed_from_delivery_id: str | None


class ListDeliveriesParams(PaginationParams, total=False):
    status: WebhookDeliveryStatus
    event_type: WebhookEventType


class WebhookEvent(TypedDict):
    version: Literal["2026-07-20"]
    event_id: str
    event_type: WebhookEventType
    created_at: str
    test: bool
    data: Any
