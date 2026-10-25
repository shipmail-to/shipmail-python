from __future__ import annotations

from typing import Literal, TypedDict

from .common import EmailRecipientInput, PaginationParams
from .message import Message


class AutoReply(TypedDict):
    enabled: bool
    subject: str | None
    body: str | None
    from_date: str | None
    to_date: str | None


MailboxSuspensionReason = Literal["billing", "manual", "security", "abuse"]


class Mailbox(TypedDict):
    object: Literal["mailbox"]
    id: str
    domain_id: str
    address: str
    display_name: str | None
    suspended_at: str | None
    suspension_reasons: list[MailboxSuspensionReason]
    auto_reply: AutoReply
    agent_security_hold: bool
    created_at: str
    updated_at: str


MailboxRuleMatchMode = Literal["all", "any"]


class _MailboxRuleConditionValue(TypedDict):
    type: Literal[
        "from_is",
        "from_contains",
        "recipient_is",
        "recipient_contains",
        "plus_tag_is",
        "subject_contains",
    ]
    value: str


class _MailboxRuleConditionFlag(TypedDict):
    type: Literal["has_attachment", "list_unsubscribe_exists"]


class _MailboxRuleConditionGroup(TypedDict):
    type: Literal["group"]
    match_mode: MailboxRuleMatchMode
    conditions: list["MailboxRuleCondition"]


MailboxRuleCondition = _MailboxRuleConditionValue | _MailboxRuleConditionFlag | _MailboxRuleConditionGroup


class _MailboxRuleMoveTargetSystem(TypedDict):
    kind: Literal["system"]
    role: Literal["inbox", "archive", "junk", "trash"]


class _MailboxRuleMoveTargetCustom(TypedDict):
    kind: Literal["custom"]
    folder_id: str


MailboxRuleMoveTarget = _MailboxRuleMoveTargetSystem | _MailboxRuleMoveTargetCustom


class _MailboxRuleActionMove(TypedDict):
    type: Literal["move"]
    target: MailboxRuleMoveTarget


class _MailboxRuleActionFlag(TypedDict):
    type: Literal["mark_read", "star", "send_webhook"]


MailboxRuleAction = _MailboxRuleActionMove | _MailboxRuleActionFlag


class MailboxRule(TypedDict):
    id: str
    name: str
    enabled: bool
    position: int
    match_mode: MailboxRuleMatchMode
    stop: bool
    conditions: list[MailboxRuleCondition]
    actions: list[MailboxRuleAction]


class MailboxRuleFolder(TypedDict):
    id: str
    name: str
    parent_id: str | None
    role: str | None
    kind: Literal["custom", "system"]


class MailboxRules(TypedDict):
    object: Literal["mailbox_rules"]
    mailbox_id: str
    address: str
    rules: list[MailboxRule]
    folders: list[MailboxRuleFolder]


class UpdateMailboxRulesParams(TypedDict):
    rules: list[MailboxRule]


MailboxExportStatus = Literal["pending", "processing", "completed", "failed", "expired"]
MailboxExportErrorCode = Literal["source_unavailable", "snapshot_changed", "export_failed"]


class MailboxExport(TypedDict):
    object: Literal["mailbox_export"]
    id: str
    mailbox_id: str
    status: MailboxExportStatus
    format: Literal["zip"]
    format_version: int
    file_size: int | None
    message_count: int | None
    folder_count: int | None
    error_code: MailboxExportErrorCode | None
    download_url: str | None
    download_url_expires_at: str | None
    expires_at: str | None
    created_at: str
    started_at: str | None
    completed_at: str | None


MailboxAppPasswordState = Literal["pending_create", "active", "pending_revoke", "revoked", "failed"]
MailboxAppPasswordPurpose = Literal["operator_client"]


class MailboxAppPassword(TypedDict):
    object: Literal["mailbox_app_password"]
    id: str
    mailbox_id: str
    name: str
    state: MailboxAppPasswordState
    purpose: MailboxAppPasswordPurpose
    expires_at: str | None
    allowed_cidrs: list[str]
    last_used_at: str | None
    created_at: str
    revoked_at: str | None


class CreatedMailboxAppPassword(MailboxAppPassword):
    secret: str


class MailboxAppPasswordList(TypedDict):
    object: Literal["list"]
    data: list[MailboxAppPassword]


class CreateMailboxAppPasswordParams(TypedDict, total=False):
    name: str
    expires_at: str
    allowed_cidrs: list[str]


class MailboxFolder(TypedDict):
    object: Literal["mailbox_folder"]
    id: str
    name: str
    parent_id: str | None
    role: str | None
    kind: Literal["custom", "system"]
    total_emails: int
    unread_emails: int
    unread_threads: int
    sort_order: int


class MailboxFolders(TypedDict):
    object: Literal["mailbox_folders"]
    mailbox_id: str
    address: str
    data: list[MailboxFolder]


class MailboxIdentity(TypedDict):
    object: Literal["mailbox_identity"]
    id: str
    name: str
    email: str


class MailboxIdentities(TypedDict):
    object: Literal["mailbox_identities"]
    mailbox_id: str
    address: str
    data: list[MailboxIdentity]


class InboxEmailHeader(TypedDict):
    name: str | None
    email: str | None


InboxKeyword = Literal["$flagged", "$seen", "$draft", "$answered", "$forwarded"]


class InboxAttachment(TypedDict):
    part_id: str
    blob_id: str
    name: str | None
    content_type: str
    size: int
    download_path: str


class InboxBodyPart(TypedDict):
    part_id: str
    type: str


class InboxBodyValue(TypedDict):
    value: str
    is_encoding_problem: bool


EmailAuthVerdict = Literal[
    "pass",
    "fail",
    "softfail",
    "neutral",
    "none",
    "temperror",
    "permerror",
    "policy",
    "unknown",
]


class EmailAuthenticationSpamResults(TypedDict):
    isSpam: bool | None
    scoreMilli: int | None


class EmailAuthenticationRawResults(TypedDict):
    authenticationResults: str | None
    receivedSpf: str | None
    spamStatus: str | None


class EmailAuthenticationResults(TypedDict):
    spf: EmailAuthVerdict
    dkim: EmailAuthVerdict
    dmarc: EmailAuthVerdict
    spam: EmailAuthenticationSpamResults
    raw: EmailAuthenticationRawResults


InboxMessageSecurityRiskCode = Literal[
    "instruction_override",
    "prompt_or_secret_disclosure",
    "role_override",
    "covert_instruction",
    "hidden_html_instruction",
    "context_exfiltration",
    "oversized_untrusted_content",
    "unauthorized_action",
]


class InboxMessageSecurityReviewInfo(TypedDict):
    decision: Literal["released"]
    released_at: str
    released_by: Literal["user", "api_key"]


class InboxMessageSecurity(TypedDict):
    status: Literal["flagged", "not_flagged", "not_scanned"]
    risk_codes: list[InboxMessageSecurityRiskCode]
    scanner: Literal["pattern_v1"]
    content_sha256: str
    review: InboxMessageSecurityReviewInfo | None


InboxMessage = TypedDict(
    "InboxMessage",
    {
        "object": Literal["inbox_message"],
        "id": str,
        "thread_id": str,
        "conversation_id": str | None,
        "mailbox_id": str,
        "address": str,
        "folder_ids": list[str],
        "keywords": dict[str, bool],
        "from": list[InboxEmailHeader] | None,
        "to": list[InboxEmailHeader] | None,
        "subject": str | None,
        "received_at": str,
        "preview": str,
        "has_attachment": bool,
        "size": int,
        "authentication_results": EmailAuthenticationResults | None,
        "security": InboxMessageSecurity,
    },
)


InboxFullMessage = TypedDict(
    "InboxFullMessage",
    {
        "object": Literal["inbox_message_full"],
        "id": str,
        "thread_id": str,
        "conversation_id": str | None,
        "mailbox_id": str,
        "address": str,
        "folder_ids": list[str],
        "keywords": dict[str, bool],
        "from": list[InboxEmailHeader] | None,
        "to": list[InboxEmailHeader] | None,
        "subject": str | None,
        "received_at": str,
        "preview": str,
        "has_attachment": bool,
        "size": int,
        "cc": list[InboxEmailHeader] | None,
        "reply_to": list[InboxEmailHeader] | None,
        "message_id": list[str] | None,
        "in_reply_to": list[str] | None,
        "references": list[str] | None,
        "body_values": dict[str, InboxBodyValue],
        "text_body": list[InboxBodyPart],
        "html_body": list[InboxBodyPart],
        "attachments": list[InboxAttachment],
        "authentication_results": EmailAuthenticationResults | None,
        "reply_text": str | None,
        "security": InboxMessageSecurity,
    },
)


class InboxMessageSecurityReview(TypedDict):
    object: Literal["inbox_message_security_review"]
    mailbox_id: str
    message_id: str
    security: InboxMessageSecurity


class InboxCursorPagination(TypedDict):
    limit: int
    total: int
    has_more: bool
    next_cursor: str | None


class InboxMessages(TypedDict):
    object: Literal["inbox_messages"]
    mailbox_id: str
    address: str
    data: list[InboxFullMessage]
    junk_total: int | None
    pagination: InboxCursorPagination


InboxThreadAttentionState = Literal[
    "needs_reply",
    "waiting_on_them",
    "done",
    "follow_up_due",
    "delivery_failed",
    "no_action",
]


class InboxThreadSummary(TypedDict):
    object: Literal["inbox_thread_summary"]
    id: str
    thread_id: str
    conversation_id: str
    attention_state: InboxThreadAttentionState
    version: int
    attention_since: str | None
    done_at: str | None
    follow_up_at: str | None
    assigned_member_id: str | None
    subject: str | None
    latest_from_address: str | None
    message_count: int
    first_message_at: str
    last_message_at: str
    latest_message_id: str | None
    latest_email_id: str | None
    latest_inbound_message_id: str | None
    latest_inbound_email_id: str | None
    latest_inbound_at: str | None
    latest_outbound_message_id: str | None
    latest_outbound_email_id: str | None
    latest_outbound_at: str | None


class InboxThreadsPagination(TypedDict):
    limit: int
    has_more: bool
    next_cursor: str | None
    snapshot_at: str


class InboxThreads(TypedDict):
    object: Literal["inbox_threads"]
    mailbox_id: str
    data: list[InboxThreadSummary]
    summary: dict[InboxThreadAttentionState, int]
    pagination: InboxThreadsPagination


class InboxThreadAttentionResult(TypedDict):
    object: Literal["inbox_thread_attention"]
    id: str
    thread_id: str
    conversation_id: str
    attention_state: InboxThreadAttentionState
    version: int
    attention_since: str | None
    done_at: str | None
    follow_up_at: str | None


class InboxDraftRecipient(TypedDict):
    address: str
    name: str | None


InboxDraft = TypedDict(
    "InboxDraft",
    {
        "object": Literal["inbox_draft"],
        # Inbox message ID: usable with get_inbox_message.
        "id": str,
        "mailbox_id": str,
        "from": InboxDraftRecipient,
        "to": list[InboxDraftRecipient],
        "cc": list[InboxDraftRecipient],
        "bcc": list[InboxDraftRecipient],
        "subject": str,
        # Formatting the HTML sanitiser dropped, such as "table" or "h4".
        "removed_formatting": list[str],
        "created_at": str,
    },
)


class InboxReplyDraft(TypedDict):
    object: Literal["inbox_reply_draft"]
    id: str
    mailbox_id: str
    thread_id: str
    conversation_id: str
    based_on_message_id: str | None
    expected_version: int
    reply_mode: Literal["reply", "reply_all"]
    status: Literal["draft", "sending", "sent", "invalidated", "failed"]
    # Empty, and subject/html/text are None, once the stored draft no longer exists.
    to: list[dict[str, str | None]]
    cc: list[dict[str, str | None]]
    subject: str | None
    html: str | None
    text: str | None
    # SHA-256 of the complete canonical subject/text/HTML snapshot; None when unavailable.
    content_sha256: str | None
    sent_message_id: str | None
    created_at: str
    updated_at: str
    sent_at: str | None


class InboxReplyDraftWrite(InboxReplyDraft):
    # Returned by create and update: formatting the HTML sanitiser dropped.
    removed_formatting: list[str]


class InboxReplyDraftList(TypedDict):
    object: Literal["list"]
    data: list[InboxReplyDraft]


class InboxReplyDraftSend(TypedDict):
    object: Literal["inbox_reply_draft_send"]
    draft_id: str
    status: Literal["draft", "sending", "sent", "invalidated", "failed"]
    message: Message


class InboxThread(TypedDict):
    object: Literal["inbox_thread"]
    mailbox_id: str
    address: str
    thread_id: str
    conversation_id: str | None
    # Current conversation version: pass it as expected_version to create_inbox_reply_draft.
    version: int | None
    data: list[InboxFullMessage]


class InboxMessageAction(TypedDict):
    object: Literal["inbox_message_action"]
    mailbox_id: str
    address: str
    message_id: str
    ok: Literal[True]
    folder_ids: list[str] | None
    keywords: dict[str, bool] | None


class MailboxForwarding(TypedDict):
    object: Literal["mailbox_forwarding"]
    id: str
    mailbox_id: str
    destination: str
    sender: str | None
    recipient: str | None
    status: Literal["pending", "active"]
    verification_sent_at: str | None
    verified_at: str | None
    created_at: str
    updated_at: str


class MailboxForwardingList(TypedDict):
    object: Literal["mailbox_forwarding_list"]
    mailbox_id: str
    data: list[MailboxForwarding]


class _CreateMailboxForwardingParamsRequired(TypedDict):
    destination: str


class CreateMailboxForwardingParams(_CreateMailboxForwardingParamsRequired, total=False):
    sender: str | None
    recipient: str | None


class _CreateMailboxParamsRequired(TypedDict):
    domain_id: str
    address: str


class CreateMailboxParams(_CreateMailboxParamsRequired, total=False):
    password: str
    generate_password: Literal[True]
    display_name: str


class UpdateMailboxParams(TypedDict, total=False):
    display_name: str | None
    agent_security_hold: bool


class CreateMailboxFolderParams(TypedDict):
    name: str
    parent_id: str | None


class UpdateMailboxFolderParams(TypedDict):
    name: str


class ResetMailboxPasswordParams(TypedDict):
    password: str


class ListMailboxesParams(PaginationParams, total=False):
    domain_id: str


# "from" is a Python keyword, so the text filters use the functional TypedDict form.
_InboxMessageTextFilters = TypedDict(
    "_InboxMessageTextFilters",
    {"from": str, "to": str, "subject": str},
    total=False,
)


class ListInboxMessagesParams(_InboxMessageTextFilters, total=False):
    folder_id: str
    folder_role: Literal["inbox", "starred", "sent", "drafts", "archive", "junk", "trash"]
    search_text: str
    has_attachment: bool
    cursor: str
    after: str
    before: str
    limit: int
    has_keyword: InboxKeyword
    not_keyword: InboxKeyword


class ListInboxThreadsParams(TypedDict, total=False):
    attention_state: InboxThreadAttentionState
    sort_by: Literal["attention_since", "last_message_at"]
    order: Literal["asc", "desc"]
    after: str
    before: str
    cursor: str
    limit: int


class _CreateInboxDraftParamsRequired(TypedDict):
    to: list[EmailRecipientInput]


class CreateInboxDraftParams(_CreateInboxDraftParamsRequired, total=False):
    cc: list[EmailRecipientInput]
    bcc: list[EmailRecipientInput]
    subject: str
    text: str
    html: str


class _CreateInboxReplyDraftParamsRequired(TypedDict):
    expected_version: int


class CreateInboxReplyDraftParams(_CreateInboxReplyDraftParamsRequired, total=False):
    text: str
    html: str
    reply_mode: Literal["reply", "reply_all"]


class UpdateInboxReplyDraftParams(TypedDict, total=False):
    # The new body replaces the old one. html alone derives the text part.
    text: str
    html: str


class _UpdateInboxThreadAttentionParamsRequired(TypedDict):
    expected_version: int


class UpdateInboxThreadAttentionParams(_UpdateInboxThreadAttentionParamsRequired, total=False):
    done: bool
    follow_up_at: str | None


class _DownloadInboxAttachmentParamsRequired(TypedDict):
    blob_id: str


class DownloadInboxAttachmentParams(_DownloadInboxAttachmentParamsRequired, total=False):
    message_id: str
    name: str


class ReleaseInboxMessageSecurityParams(TypedDict):
    decision: Literal["release"]
    reason: str
    expected_content_sha256: str


class UpdateInboxMessageParams(TypedDict, total=False):
    read: bool
    starred: bool


class MoveInboxMessageParams(TypedDict, total=False):
    from_folder_id: str
    target_role: Literal["inbox", "archive", "junk", "trash"]
    target_folder_id: str


class _UpdateAutoReplyParamsRequired(TypedDict):
    enabled: bool


class UpdateAutoReplyParams(_UpdateAutoReplyParamsRequired, total=False):
    subject: str | None
    body: str | None
    from_date: str | None
    to_date: str | None


MailboxDeliveryDestinationStatus = Literal[
    "available",
    "out_of_office",
    "suspended",
    "archived",
    "unavailable",
]


class MailboxDeliveryDestination(TypedDict):
    id: str
    address: str
    display_name: str | None
    status: MailboxDeliveryDestinationStatus
    out_of_office_end_at: str | None
    responsible_member_count: int
    push_ready_member_count: int


class _MailboxDeliveryRoutingBase(TypedDict):
    object: Literal["mailbox_delivery_routing"]
    mailbox_id: str
    source_address: str
    destinations: list[MailboxDeliveryDestination]


class _MailboxDeliveryRoutingKeep(_MailboxDeliveryRoutingBase):
    mode: Literal["keep"]


class _MailboxDeliveryRoutingFixed(_MailboxDeliveryRoutingBase):
    mode: Literal["fixed"]
    destination_mailbox_id: str
    fallback_mailbox_id: str
    activation_state: Literal["pending", "active", "failed"]
    activation_error: str | None


class _MailboxDeliveryRoutingRoundRobin(_MailboxDeliveryRoutingBase):
    mode: Literal["round_robin"]
    destination_mailbox_ids: list[str]
    fallback_mailbox_id: str
    activation_state: Literal["pending", "active", "failed"]
    activation_error: str | None


MailboxDeliveryRouting = (
    _MailboxDeliveryRoutingKeep | _MailboxDeliveryRoutingFixed | _MailboxDeliveryRoutingRoundRobin
)


class _UpdateMailboxDeliveryRoutingKeep(TypedDict):
    mode: Literal["keep"]


class _UpdateMailboxDeliveryRoutingFixed(TypedDict):
    mode: Literal["fixed"]
    destination_mailbox_id: str
    fallback_mailbox_id: str


class _UpdateMailboxDeliveryRoutingRoundRobin(TypedDict):
    mode: Literal["round_robin"]
    destination_mailbox_ids: list[str]
    fallback_mailbox_id: str


UpdateMailboxDeliveryRoutingParams = (
    _UpdateMailboxDeliveryRoutingKeep
    | _UpdateMailboxDeliveryRoutingFixed
    | _UpdateMailboxDeliveryRoutingRoundRobin
)


MailboxImportStatus = Literal[
    "queued",
    "running",
    "paused_throttle",
    "paused_quota",
    "completed",
    "failed",
    "cancelled",
    "undo_queued",
    "undoing",
    "undone",
    "undo_failed",
]

MailboxImportProvider = Literal[
    "gmail",
    "outlook",
    "yahoo",
    "aol",
    "icloud",
    "fastmail",
    "zoho",
    "titan",
    "namecheap",
    "migadu",
    "gmx",
    "mail_com",
    "mailbox_org",
    "mxroute",
    "infomaniak",
    "ovh",
    "gandi",
    "imap",
    "takeout",
    "proton",
    "tuta",
    "file",
]

MailboxImportImapProvider = Literal[
    "gmail",
    "yahoo",
    "aol",
    "icloud",
    "fastmail",
    "zoho",
    "titan",
    "namecheap",
    "migadu",
    "gmx",
    "mail_com",
    "mailbox_org",
    "mxroute",
    "infomaniak",
    "ovh",
    "gandi",
    "imap",
]

MailboxImportFileProvider = Literal["takeout", "proton", "tuta", "file"]

# "skipped": the source server refused the folder; the import finished without it.
MailboxImportFolderState = Literal["pending", "importing", "completed", "failed", "skipped"]

MailboxImportRange = Literal["all", "12m", "3m", "1m"]

MailboxImportKind = Literal["imap", "file"]


class MailboxImportCounts(TypedDict):
    found: int
    imported: int
    undone: int
    duplicates_skipped: int
    oversize_skipped: int
    failed: int
    contacts_imported: int


class MailboxImportBytes(TypedDict):
    total: int
    imported: int


class MailboxImportFolder(TypedDict):
    source_folder: str
    target_folder: str | None
    role: str | None
    state: MailboxImportFolderState
    found: int
    imported: int
    duplicates: int
    oversize: int
    failed: int


class _MailboxImportRequired(TypedDict):
    object: Literal["import"]
    id: str
    mailbox_id: str
    kind: MailboxImportKind
    provider: MailboxImportProvider
    source_address: str | None
    status: MailboxImportStatus
    status_detail: str | None
    error: str | None
    resume_at: str | None
    counts: MailboxImportCounts
    bytes: MailboxImportBytes
    created_at: str
    started_at: str | None
    completed_at: str | None


class MailboxImportSourceRetention(TypedDict):
    state: Literal["available", "missing", "expired", "deleted", "not_applicable"]
    expires_at: str | None
    deleted_at: str | None


class MailboxImport(_MailboxImportRequired, total=False):
    folders: list[MailboxImportFolder]
    source_retention: MailboxImportSourceRetention


class MailboxImports(TypedDict):
    object: Literal["imports"]
    mailbox_id: str
    data: list[MailboxImport]


class _MailboxImportImapSourceRequired(TypedDict):
    type: Literal["imap"]
    provider: MailboxImportImapProvider
    email: str
    password: str


class MailboxImportImapSource(_MailboxImportImapSourceRequired, total=False):
    host: str
    port: int


class MailboxImportFileSource(TypedDict):
    type: Literal["files"]
    provider: MailboxImportFileProvider
    file_ids: list[str]


MailboxImportSource = MailboxImportImapSource | MailboxImportFileSource


class MailboxImportOptions(TypedDict, total=False):
    folders: list[str] | None
    range: MailboxImportRange
    include_spam: bool
    include_trash: bool


class _CreateMailboxImportParamsRequired(TypedDict):
    source: MailboxImportSource


class CreateMailboxImportParams(_CreateMailboxImportParamsRequired, total=False):
    options: MailboxImportOptions


class CreateImportUploadParams(TypedDict):
    provider: MailboxImportFileProvider
    file_name: str
    size_bytes: int


class RestoreMailboxImportParams(TypedDict):
    file_ids: list[str]


class ImportUploadPart(TypedDict):
    part_number: int
    upload_url: str


class ImportUpload(TypedDict):
    object: Literal["import_upload"]
    file_id: str
    part_size_bytes: int
    parts: list[ImportUploadPart]
    expires_in_seconds: int


class CompleteImportUploadPart(TypedDict):
    part_number: int
    etag: str


class CompleteImportUploadParams(TypedDict):
    parts: list[CompleteImportUploadPart]
