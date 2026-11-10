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


# Why an automation would not run, in the order they are checked. message_not_live,
# mailbox_not_in_trigger and message_in_junk appear only in a test result. See the TypeScript SDK
# or the docs for each.
AutomationBlockedReason = Literal[
    "automation_not_active",
    "no_active_version",
    "invalid_definition",
    "policy_version_outdated",
    "trigger_mailbox_outside_scope",
    "owner_unavailable",
    "message_not_live",
    "mailbox_not_in_trigger",
    "message_in_junk",
    "models_disabled",
    "model_budget_exhausted",
]

# Why a Send-mode automation runs, but writes drafts instead of sending.
AutomationSendDegradedReason = Literal["automatic_send_disabled", "writing_style_required"]


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
    # True when blocked_reasons is empty: it would run now.
    runnable: bool
    blocked_reasons: list[AutomationBlockedReason]
    # Runs, but writes drafts instead of sending. Empty unless a Send-mode automation would only draft.
    send_degraded_reasons: list[AutomationSendDegradedReason]
    created_at: str
    updated_at: str


class TestAutomationParams(TypedDict):
    mailbox_id: str
    # An inbox message id in that mailbox.
    message_id: str


class AutomationTestCondition(TypedDict):
    index: int
    type: str
    # None when the condition was not evaluated.
    matched: bool | None
    # The classifier's confidence for a semantic condition, else None.
    confidence: float | None
    not_evaluated_reason: (
        Literal["earlier_condition_failed", "models_disabled", "model_budget_exhausted", "classifier_failed"]
        | None
    )


class AutomationTestAction(TypedDict):
    index: int
    type: str


class AutomationTest(TypedDict):
    # A dry run of an automation on one stored message. Nothing is changed, queued or sent.
    object: Literal["automation_test"]
    automation_id: str
    mailbox_id: str
    message_id: str
    runnable: bool
    blocked_reasons: list[AutomationBlockedReason]
    # Runs, but writes drafts instead of sending.
    send_degraded_reasons: list[AutomationSendDegradedReason]
    conditions: list[AutomationTestCondition]
    # None when a condition could not be evaluated.
    conditions_matched: bool | None
    would_run: bool
    mode: Literal["draft", "send"]
    actions: list[AutomationTestAction]
    # Classifier calls this test made. They count against the AI budget.
    model_calls: int


class CreateAutomationParams(TypedDict):
    name: str
    definition: AutomationDefinition


class UpdateAutomationParams(TypedDict, total=False):
    name: str
    definition: AutomationDefinition
    status: AutomationStatus


class ListAutomationsResponse(TypedDict):
    data: list[Automation]
