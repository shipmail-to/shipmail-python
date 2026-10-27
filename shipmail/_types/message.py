from __future__ import annotations

from typing import Literal, TypedDict

from .common import (
    DataMode,
    EmailRecipient,
    EmailRecipientInput,
    MessageSource,
    MessageStatus,
    PaginationParams,
    SandboxOutcome,
)
from .template import SendMessageTemplate


class AttachmentMetadata(TypedDict):
    filename: str
    size: int
    content_type: str


class MessageRuleDisposition(TypedDict):
    matched_rule_ids: list[str]
    stop_rule_id: str | None


class Message(TypedDict):
    object: Literal["message"]
    id: str
    mailbox_id: str
    thread_id: str | None
    conversation_id: str | None
    source_rfc_message_id: str | None
    delivered_rfc_message_id: str | None
    client_reference: str | None
    metadata: dict[str, str | int | float | bool | None]
    headers: list[OutboundHeader]
    subject: str | None
    from_address: str | None
    to_addresses: list[EmailRecipient] | None
    cc_addresses: list[EmailRecipient] | None
    bcc_addresses: list[EmailRecipient] | None
    attachments: list[AttachmentMetadata] | None
    source: MessageSource
    mode: DataMode
    status: MessageStatus
    rule_disposition: MessageRuleDisposition | None
    scheduled_at: str | None
    created_at: str
    updated_at: str


class _AttachmentRequired(TypedDict):
    filename: str
    content: str


class Attachment(_AttachmentRequired, total=False):
    content_type: str


class StagedAttachment(TypedDict):
    object: Literal["staged_attachment"]
    id: str
    mailbox_id: str
    filename: str
    content_type: str
    size: int
    sha256: str
    expires_at: str


class PrepareStagedAttachmentUploadParams(TypedDict):
    filename: str
    content_type: str
    size: int
    sha256: str


class StagedAttachmentUpload(TypedDict):
    object: Literal["staged_attachment_upload"]
    mailbox_id: str
    filename: str
    content_type: str
    size: int
    sha256: str
    upload_url: str
    expires_at: str


class OutboundHeader(TypedDict):
    name: str
    value: str


class _SendMessageRequired(TypedDict):
    to: list[EmailRecipientInput]


# "hello@example.com" or "Acme Support <hello@example.com>".
# For a transactional sender, pass the bare sender address. Shipmail adds its name and Reply-To.
_SendMessageFrom = TypedDict("_SendMessageFrom", {"from": str}, total=False)


class SendMessageParams(_SendMessageRequired, _SendMessageFrom, total=False):
    mailbox_id: str
    subject: str
    cc: list[EmailRecipientInput]
    bcc: list[EmailRecipientInput]
    reply_to: EmailRecipientInput
    html: str
    text: str
    # A stored template. With it, omit subject, html and text.
    template: SendMessageTemplate
    in_reply_to: str
    references: list[str]
    attachments: list[Attachment]
    staged_attachment_ids: list[str]
    client_reference: str
    metadata: dict[str, str | int | float | bool | None]
    source_rfc_message_id: str
    headers: list[OutboundHeader]
    scheduled_at: str
    track_reply: bool
    sandbox_outcome: SandboxOutcome


class _ScheduledMessageRequired(TypedDict):
    object: Literal["scheduled_message"]
    id: str
    scheduled_message_id: str
    kind: Literal["scheduled", "undo"]
    mailbox_id: str
    mailbox_address: str
    from_address: str
    identity_id: str
    mode: DataMode
    subject: str
    to: list[EmailRecipient]
    cc: list[EmailRecipient]
    bcc: list[EmailRecipient]
    attachments: list[AttachmentMetadata]
    scheduled_at: str
    created_at: str
    updated_at: str
    last_error: str | None


class ScheduledMessageUploadedAttachment(TypedDict):
    blob_id: str
    filename: str
    content_type: str
    size: int


class ScheduledMessage(_ScheduledMessageRequired, total=False):
    # "settling": a send attempt may already have gone out and is being checked; the message
    # cannot be updated or cancelled until that resolves. Absent from servers older than the field.
    status: Literal["scheduled", "settling"]
    draft_email_id: str
    from_name: str
    text: str
    html: str
    in_reply_to: str | None
    references: list[str]
    uploaded_attachments: list[ScheduledMessageUploadedAttachment]


class ScheduledMessageList(TypedDict):
    object: Literal["scheduled_message_list"]
    data: list[ScheduledMessage]
    total: int


class ListScheduledMessagesParams(TypedDict, total=False):
    include_held: bool
    search: str
    limit: int


class _UpdateScheduledMessageRequired(TypedDict):
    to: list[EmailRecipientInput]
    subject: str
    scheduled_at: str


class UpdateScheduledMessageParams(_UpdateScheduledMessageRequired, total=False):
    cc: list[EmailRecipientInput]
    bcc: list[EmailRecipientInput]
    html: str
    text: str
    in_reply_to: str
    references: list[str]
    staged_attachment_ids: list[str]


class ListMessagesParams(PaginationParams, total=False):
    mailbox_id: str
    client_reference: str


class MessageAnalytics(TypedDict):
    object: Literal["message_analytics"]
    id: str
    mailbox_id: str
    thread_id: str | None
    conversation_id: str | None
    client_reference: str | None
    direction: Literal["inbound", "outbound"]
    contact_addresses: list[str]
    recipient_count: int
    attachment_count: int
    source: MessageSource
    mode: DataMode
    status: MessageStatus
    scheduled_at: str | None
    created_at: str
    updated_at: str


class ListMessageAnalyticsParams(PaginationParams, total=False):
    updated_after: str
    updated_before: str


class MessageAnalyticsPagination(TypedDict):
    next_cursor: str | None
    has_more: bool
    limit: int
    snapshot_at: str


class MessageAnalyticsPage(TypedDict):
    data: list[MessageAnalytics]
    pagination: MessageAnalyticsPagination


class _ReplyToMessageRequired(TypedDict):
    to: list[EmailRecipientInput]


class ReplyToMessageParams(_ReplyToMessageRequired, total=False):
    html: str
    text: str
    cc: list[EmailRecipientInput]
    bcc: list[EmailRecipientInput]
    client_reference: str
    metadata: dict[str, str | int | float | bool | None]
    source_rfc_message_id: str
    headers: list[OutboundHeader]
    scheduled_at: str
    track_reply: bool
    sandbox_outcome: SandboxOutcome


class _InjectSandboxInboundRequired(TypedDict):
    from_: EmailRecipientInput
    subject: str


class InjectSandboxInboundParams(_InjectSandboxInboundRequired, total=False):
    to: list[EmailRecipientInput]
    cc: list[EmailRecipientInput]
    text: str
    html: str
    message_id: str
    in_reply_to: str
    references: list[str]
    received_at: str
    headers: list[OutboundHeader]
