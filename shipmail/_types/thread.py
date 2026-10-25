from __future__ import annotations

from typing import Literal, TypedDict

from .common import EmailRecipientInput, PaginationParams, SandboxOutcome
from .message import Message


class Thread(TypedDict):
    object: Literal["thread"]
    id: str
    conversation_id: str
    mailbox_id: str
    subject: str | None
    message_count: int
    latest_message: Message
    created_at: str
    updated_at: str


class ListThreadsParams(PaginationParams, total=False):
    mailbox_id: str


class _GetThreadRequired(TypedDict):
    mailbox_id: str


class GetThreadParams(_GetThreadRequired, total=False):
    cursor: str
    limit: int


class _ReplyToThreadRequired(TypedDict):
    mailbox_id: str
    to: list[EmailRecipientInput]


class ReplyToThreadParams(_ReplyToThreadRequired, total=False):
    html: str
    text: str
    cc: list[EmailRecipientInput]
    scheduled_at: str
    track_reply: bool
    sandbox_outcome: SandboxOutcome
