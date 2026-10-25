from __future__ import annotations

from typing import Literal, TypedDict

AutomationStatus = Literal["active", "paused", "disabled"]
AutomationRunStatus = Literal[
    "queued", "running", "completed", "failed", "degraded", "cancelled", "skipped"
]


class EmailReceivedTrigger(TypedDict):
    type: Literal["email_received"]
    mailbox_ids: list[str]


class ScheduledTrigger(TypedDict):
    type: Literal["scheduled"]
    cron: str
    time_zone: str


class ManualTrigger(TypedDict):
    type: Literal["manual"]
    mailbox_ids: list[str]


class ThreadStateTrigger(TypedDict):
    type: Literal["thread_state"]
    mailbox_ids: list[str]
    state: Literal["no_reply_after"]
    duration_minutes: int


AutomationTrigger = EmailReceivedTrigger | ScheduledTrigger | ManualTrigger | ThreadStateTrigger


class SenderAddressCondition(TypedDict):
    type: Literal["sender_address"]
    addresses: list[str]


class SenderDomainCondition(TypedDict):
    type: Literal["sender_domain"]
    domains: list[str]


class SubjectContainsCondition(TypedDict):
    type: Literal["subject_contains"]
    values: list[str]


class HasAttachmentCondition(TypedDict):
    type: Literal["has_attachment"]
    value: bool


class SemanticPositiveMatchCondition(TypedDict):
    type: Literal["semantic_positive_match"]
    instruction: str
    minimum_confidence: float


AutomationCondition = (
    SenderAddressCondition
    | SenderDomainCondition
    | SubjectContainsCondition
    | HasAttachmentCondition
    | SemanticPositiveMatchCondition
)


class CreateReplyDraftAction(TypedDict):
    type: Literal["create_reply_draft"]
    instruction: str


class ReplyToTriggerSenderAction(TypedDict):
    type: Literal["reply_to_trigger_sender"]
    instruction: str


class ArchiveTriggerMessageAction(TypedDict):
    type: Literal["archive_trigger_message"]


class MoveTriggerMessageAction(TypedDict):
    type: Literal["move_trigger_message"]
    mailbox_id: str
    destination_folder_id: str


class SetTriggerReadStateAction(TypedDict):
    type: Literal["set_trigger_read_state"]
    is_read: bool


class SetTriggerStarStateAction(TypedDict):
    type: Literal["set_trigger_star_state"]
    is_starred: bool


class GenerateMailReportAction(TypedDict):
    type: Literal["generate_mail_report"]
    metric: Literal["received", "sent", "unread"]
    lookback_minutes: int


AutomationAction = (
    CreateReplyDraftAction
    | ReplyToTriggerSenderAction
    | ArchiveTriggerMessageAction
    | MoveTriggerMessageAction
    | SetTriggerReadStateAction
    | SetTriggerStarStateAction
    | GenerateMailReportAction
)


class AutomationScope(TypedDict):
    mailbox_ids: list[str]
    calendar_addresses: list[str]


class AutomationDefinition(TypedDict):
    trigger: AutomationTrigger
    conditions: list[AutomationCondition]
    actions: list[AutomationAction]
    mode: Literal["draft", "send"]
    scope: AutomationScope


class AutomationRunSummary(TypedDict):
    object: Literal["automation_run"]
    id: str
    status: AutomationRunStatus
    error_code: str | None
    created_at: str


class AutomationRun(TypedDict):
    object: Literal["automation_run"]
    id: str
    automation_id: str
    status: AutomationRunStatus


class Automation(TypedDict):
    object: Literal["automation"]
    id: str
    name: str
    status: AutomationStatus
    version_id: str
    version: int
    definition: AutomationDefinition
    last_run: AutomationRunSummary | None
    next_run_at: str | None
    created_at: str
    updated_at: str


class CreateAutomationParams(TypedDict):
    name: str
    definition: AutomationDefinition


class UpdateAutomationParams(TypedDict, total=False):
    name: str
    definition: AutomationDefinition
    status: AutomationStatus


class ListAutomationsResponse(TypedDict):
    data: list[Automation]
