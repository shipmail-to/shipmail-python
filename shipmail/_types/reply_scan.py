from __future__ import annotations

from typing import Literal, TypedDict

ReplyScanStatus = Literal["completed"]


class ReplyScan(TypedDict):
    object: Literal["reply_scan"]
    id: str
    mailbox_ids: list[str]
    after: str
    before: str
    snapshot_at: str
    status: ReplyScanStatus
    candidate_count: int
    completed_at: str
    created_at: str


class ReplyScanCandidate(TypedDict):
    object: Literal["reply_scan_candidate"]
    id: str
    mailbox_id: str
    thread_id: str
    conversation_id: str
    tracked_thread_id: str
    latest_message_id: str | None
    latest_email_id: str | None
    latest_inbound_message_id: str | None
    latest_inbound_email_id: str | None
    version: int
    attention_since: str
    subject: str | None


class ReplyScanResultsPagination(TypedDict):
    limit: int
    has_more: bool
    next_cursor: str | None


class ReplyScanResults(TypedDict):
    object: Literal["reply_scan_results"]
    scan_id: str
    data: list[ReplyScanCandidate]
    pagination: ReplyScanResultsPagination


class _CreateReplyScanParamsRequired(TypedDict):
    mailbox_ids: list[str]
    after: str


class CreateReplyScanParams(_CreateReplyScanParamsRequired, total=False):
    before: str


class ListReplyScanResultsParams(TypedDict, total=False):
    cursor: str
    limit: int
