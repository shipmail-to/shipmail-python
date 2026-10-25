from __future__ import annotations

from typing import Any, Literal, TypedDict, Union

DataMode = Literal["live", "test"]
SandboxOutcome = Literal["delivered", "bounced", "complained"]


ErrorType = Literal[
    "validation_error",
    "authentication_error",
    "authorization_error",
    "quota_exceeded",
    "not_found",
    "rate_limit_error",
    "conflict",
    "internal_error",
]

DOMAIN_STATUSES = ("pending", "verifying", "verified", "degraded", "failed")
DomainStatus = Literal["pending", "verifying", "verified", "degraded", "failed"]

MESSAGE_STATUSES = (
    "scheduled",
    "queued",
    "sent",
    "delivered",
    "bounced",
    "complained",
    "failed",
    "suppressed",
    "cancelled",
)
MessageStatus = Literal[
    "scheduled",
    "queued",
    "sent",
    "delivered",
    "bounced",
    "complained",
    "failed",
    "suppressed",
    "cancelled",
]

MESSAGE_SOURCES = ("api", "newsletter", "dashboard", "inbound", "smtp", "assistant")
MessageSource = Literal["api", "newsletter", "dashboard", "inbound", "smtp", "assistant"]

WEBHOOK_EVENT_TYPES = (
    "message.received",
    "message.sent",
    "message.delayed",
    "message.delivered",
    "message.bounced",
    "message.complained",
    "mailbox.rule_matched",
    "mailbox.export.completed",
    "mailbox.export.failed",
    "domain.verified",
    "domain.verification_failed",
    "domain.degraded",
    "org.reputation_warning",
    "org.sending_throttled",
    "org.sending_suspended",
    "org.reputation_recovered",
    "reply.overdue",
    "conversation.needs_action",
    "calendar.event_starting",
    "booking.created",
    "subscriber.added",
    "newsletter.sent",
)
WebhookEventType = Literal[
    "message.received",
    "message.sent",
    "message.delayed",
    "message.delivered",
    "message.bounced",
    "message.complained",
    "mailbox.rule_matched",
    "mailbox.export.completed",
    "mailbox.export.failed",
    "domain.verified",
    "domain.verification_failed",
    "domain.degraded",
    "org.reputation_warning",
    "org.sending_throttled",
    "org.sending_suspended",
    "org.reputation_recovered",
    "reply.overdue",
    "conversation.needs_action",
    "calendar.event_starting",
    "booking.created",
    "subscriber.added",
    "newsletter.sent",
]

WEBHOOK_DELIVERY_EVENT_TYPES = ("webhook.test", *WEBHOOK_EVENT_TYPES)
WebhookDeliveryEventType = Literal[
    "webhook.test",
    "message.received",
    "message.sent",
    "message.delayed",
    "message.delivered",
    "message.bounced",
    "message.complained",
    "mailbox.rule_matched",
    "mailbox.export.completed",
    "mailbox.export.failed",
    "domain.verified",
    "domain.verification_failed",
    "domain.degraded",
    "org.reputation_warning",
    "org.sending_throttled",
    "org.sending_suspended",
    "org.reputation_recovered",
    "reply.overdue",
    "conversation.needs_action",
    "calendar.event_starting",
    "booking.created",
    "subscriber.added",
    "newsletter.sent",
]

WEBHOOK_DELIVERY_STATUSES = ("pending", "delivered", "failed")
WebhookDeliveryStatus = Literal["pending", "delivered", "failed"]


class PaginationParams(TypedDict, total=False):
    cursor: str
    limit: int


class Pagination(TypedDict):
    next_cursor: str | None
    has_more: bool
    limit: int


class PaginatedResponse(TypedDict):
    data: list[Any]
    pagination: Pagination


class _EmailRecipientRequired(TypedDict):
    address: str


class EmailRecipient(_EmailRecipientRequired, total=False):
    name: str | None


EmailRecipientInput = Union[EmailRecipient, str]


class _ApiErrorDetailRequired(TypedDict):
    field: str
    message: str


class ApiErrorDetail(_ApiErrorDetailRequired, total=False):
    code: str


class ErrorLimit(TypedDict):
    """The plan, trial or fixed limit that refused a request. Storage values are bytes."""

    # What is limited, such as mailboxes, sends or audience_subscribers.
    resource: str
    used: float
    limit: float
    # trial until the trial ends, plan until the plan or its add-ons grow, fixed
    # for the same cap on every plan. Later servers may add values.
    scope: str


class ApiErrorInfo(TypedDict, total=False):
    type: str
    message: str
    request_id: str
    details: list[ApiErrorDetail]
    retry_after: float
    # Present only on a reconciliation_required error: the tracking message the
    # interrupted send attempt left behind.
    message_id: str
    # Present only on a refusal an organization owner can lift in Shipmail: one of
    # owner_confirmation_required, subscription_required, trial_capacity or
    # purchased_capacity. Later servers may add values.
    reason: str
    # Present with reason: the Shipmail page where the owner reviews and confirms.
    action_url: str
    # Present on a quota_exceeded error caused by a plan, trial or fixed limit.
    limit: ErrorLimit


class ApiErrorBody(TypedDict):
    error: ApiErrorInfo


class StatusResponse(TypedDict):
    status: str
    version: str
    time: str
    request_id: str


class MethodOptions(TypedDict, total=False):
    timeout: float
    headers: dict[str, str]
    idempotency_key: str


class OneTimeSecretMethodOptions(TypedDict, total=False):
    timeout: float
    headers: dict[str, str]


class ShipmailConfig(TypedDict, total=False):
    api_key: str
    base_url: str
    max_retries: int
    timeout: float
    default_headers: dict[str, str]
