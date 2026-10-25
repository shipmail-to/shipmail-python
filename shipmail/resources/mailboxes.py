from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, OneTimeSecretMethodOptions, PaginatedResponse
    from .._types.mailbox import (
        CompleteImportUploadParams,
        CreatedMailboxAppPassword,
        CreateImportUploadParams,
        CreateInboxDraftParams,
        CreateInboxReplyDraftParams,
        CreateMailboxAppPasswordParams,
        CreateMailboxFolderParams,
        CreateMailboxForwardingParams,
        CreateMailboxImportParams,
        CreateMailboxParams,
        DownloadInboxAttachmentParams,
        ImportUpload,
        InboxDraft,
        InboxFullMessage,
        InboxMessageAction,
        InboxMessages,
        InboxMessageSecurityReview,
        InboxReplyDraft,
        InboxReplyDraftList,
        InboxReplyDraftSend,
        InboxReplyDraftWrite,
        InboxThread,
        InboxThreadAttentionResult,
        InboxThreads,
        ListInboxMessagesParams,
        ListInboxThreadsParams,
        ListMailboxesParams,
        Mailbox,
        MailboxAppPasswordList,
        MailboxDeliveryRouting,
        MailboxExport,
        MailboxFolder,
        MailboxFolders,
        MailboxForwarding,
        MailboxForwardingList,
        MailboxIdentities,
        MailboxImport,
        MailboxImports,
        MailboxRules,
        MoveInboxMessageParams,
        RestoreMailboxImportParams,
        ResetMailboxPasswordParams,
        ReleaseInboxMessageSecurityParams,
        UpdateAutoReplyParams,
        UpdateInboxMessageParams,
        UpdateInboxReplyDraftParams,
        UpdateInboxThreadAttentionParams,
        UpdateMailboxFolderParams,
        UpdateMailboxParams,
        UpdateMailboxDeliveryRoutingParams,
        UpdateMailboxRulesParams,
    )
    from .._types.message import (
        InjectSandboxInboundParams,
        Message,
        PrepareStagedAttachmentUploadParams,
        ReplyToMessageParams,
        StagedAttachment,
        StagedAttachmentUpload,
    )


class SyncMailboxes:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def prepare_staged_attachment_upload(
        self,
        id: str,
        params: PrepareStagedAttachmentUploadParams,
        options: OneTimeSecretMethodOptions | None = None,
    ) -> StagedAttachmentUpload:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/staged-attachment-upload-tokens",
                body=params,
                method_options=options,
            )
        )

    def stage_attachment(
        self,
        id: str,
        *,
        filename: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        options: MethodOptions | None = None,
    ) -> StagedAttachment:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/staged-attachments",
                query={"filename": filename},
                raw_body=data,
                content_type=content_type,
                method_options=options,
            )
        )

    def inject_sandbox_inbound(
        self,
        id: str,
        params: InjectSandboxInboundParams | dict[str, object],
        options: MethodOptions | None = None,
    ) -> Message:
        body = dict(params)
        if "from_" in body:
            body["from"] = body.pop("from_")
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/sandbox/inbound",
                body=body,
                method_options=options,
            )
        )

    def create(self, params: CreateMailboxParams, options: MethodOptions | None = None) -> Mailbox:
        return self._client.request(
            RequestOptions(method="POST", path="/mailboxes", body=params, method_options=options)
        )

    def list(
        self, params: ListMailboxesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/mailboxes",
                query={
                    "domain_id": params.get("domain_id") if params else None,
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, domain_id: str | None = None, limit: int | None = None) -> SyncPage[Mailbox]:
        return SyncPage(self._client, "/mailboxes", {"domain_id": domain_id, "limit": limit})

    def get(self, id: str, options: MethodOptions | None = None) -> Mailbox:
        return self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}", method_options=options)
        )

    def update(self, id: str, params: UpdateMailboxParams, options: MethodOptions | None = None) -> Mailbox:
        return self._client.request(
            RequestOptions(method="PATCH", path=f"/mailboxes/{quote(id, safe='')}", body=params, method_options=options)
        )

    def delete(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(method="DELETE", path=f"/mailboxes/{quote(id, safe='')}", method_options=options)
        )

    def suspend(self, id: str, options: MethodOptions | None = None) -> Mailbox:
        return self._client.request(
            RequestOptions(method="POST", path=f"/mailboxes/{quote(id, safe='')}/suspend", method_options=options)
        )

    def resume(self, id: str, options: MethodOptions | None = None) -> Mailbox:
        return self._client.request(
            RequestOptions(method="POST", path=f"/mailboxes/{quote(id, safe='')}/resume", method_options=options)
        )

    def create_export(self, id: str, options: MethodOptions | None = None) -> MailboxExport:
        return self._client.request(
            RequestOptions(method="POST", path=f"/mailboxes/{quote(id, safe='')}/exports", method_options=options)
        )

    def get_export(self, id: str, export_id: str, options: MethodOptions | None = None) -> MailboxExport:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/exports/{quote(export_id, safe='')}",
                method_options=options,
            )
        )

    def list_folders(self, id: str, options: MethodOptions | None = None) -> MailboxFolders:
        return self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/folders", method_options=options)
        )

    def get_rules(self, id: str, options: MethodOptions | None = None) -> MailboxRules:
        return self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/rules", method_options=options)
        )

    def update_rules(
        self, id: str, params: UpdateMailboxRulesParams, options: MethodOptions | None = None
    ) -> MailboxRules:
        return self._client.request(
            RequestOptions(
                method="PUT", path=f"/mailboxes/{quote(id, safe='')}/rules", body=params, method_options=options
            )
        )

    def create_folder(
        self, id: str, params: CreateMailboxFolderParams, options: MethodOptions | None = None
    ) -> MailboxFolder:
        return self._client.request(
            RequestOptions(
                method="POST", path=f"/mailboxes/{quote(id, safe='')}/folders", body=params, method_options=options
            )
        )

    def update_folder(
        self, id: str, folder_id: str, params: UpdateMailboxFolderParams, options: MethodOptions | None = None
    ) -> MailboxFolder:
        return self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/mailboxes/{quote(id, safe='')}/folders/{quote(folder_id, safe='')}",
                body=params,
                method_options=options,
            )
        )

    def delete_folder(self, id: str, folder_id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/folders/{quote(folder_id, safe='')}",
                method_options=options,
            )
        )

    def list_identities(self, id: str, options: MethodOptions | None = None) -> MailboxIdentities:
        return self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/identities", method_options=options)
        )

    def list_inbox_messages(
        self,
        id: str,
        params: ListInboxMessagesParams | None = None,
        options: MethodOptions | None = None,
    ) -> InboxMessages:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages",
                query={
                    "folder_id": params.get("folder_id") if params else None,
                    "folder_role": params.get("folder_role") if params else None,
                    "search_text": params.get("search_text") if params else None,
                    "from": params.get("from") if params else None,
                    "to": params.get("to") if params else None,
                    "subject": params.get("subject") if params else None,
                    "has_attachment": params.get("has_attachment") if params else None,
                    "cursor": params.get("cursor") if params else None,
                    "after": params.get("after") if params else None,
                    "before": params.get("before") if params else None,
                    "limit": params.get("limit") if params else None,
                    "has_keyword": params.get("has_keyword") if params else None,
                    "not_keyword": params.get("not_keyword") if params else None,
                },
                method_options=options,
            )
        )

    def get_inbox_message(self, id: str, message_id: str, options: MethodOptions | None = None) -> InboxFullMessage:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}",
                method_options=options,
            )
        )

    def release_inbox_message_security(
        self,
        id: str,
        message_id: str,
        params: ReleaseInboxMessageSecurityParams,
        options: MethodOptions | None = None,
    ) -> InboxMessageSecurityReview:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}/security-review",
                body=params,
                method_options=options,
            )
        )

    def list_inbox_threads(
        self,
        id: str,
        params: ListInboxThreadsParams | None = None,
        options: MethodOptions | None = None,
    ) -> InboxThreads:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads",
                query={
                    "attention_state": params.get("attention_state") if params else None,
                    "sort_by": params.get("sort_by") if params else None,
                    "order": params.get("order") if params else None,
                    "after": params.get("after") if params else None,
                    "before": params.get("before") if params else None,
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def get_inbox_thread(self, id: str, thread_id: str, options: MethodOptions | None = None) -> InboxThread:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}",
                method_options=options,
            )
        )

    def update_inbox_thread_attention(
        self,
        id: str,
        thread_id: str,
        params: UpdateInboxThreadAttentionParams,
        options: MethodOptions | None = None,
    ) -> InboxThreadAttentionResult:
        return self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}",
                body=params,
                method_options=options,
            )
        )

    def create_inbox_draft(
        self,
        id: str,
        params: CreateInboxDraftParams,
        options: MethodOptions | None = None,
    ) -> InboxDraft:
        """Save a new message to the mailbox's Drafts folder. It is never sent by this call."""
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/drafts",
                body=params,
                method_options=options,
            )
        )

    def create_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        params: CreateInboxReplyDraftParams,
        options: MethodOptions | None = None,
    ) -> InboxReplyDraftWrite:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}/drafts",
                body=params,
                method_options=options,
            )
        )

    def list_inbox_reply_drafts(
        self, id: str, thread_id: str, options: MethodOptions | None = None
    ) -> InboxReplyDraftList:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}/drafts",
                method_options=options,
            )
        )

    def get_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        draft_id: str,
        options: MethodOptions | None = None,
    ) -> InboxReplyDraft:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=(
                    f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}"
                    f"/drafts/{quote(draft_id, safe='')}"
                ),
                method_options=options,
            )
        )

    def update_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        draft_id: str,
        params: UpdateInboxReplyDraftParams,
        options: MethodOptions | None = None,
    ) -> InboxReplyDraftWrite:
        return self._client.request(
            RequestOptions(
                method="PATCH",
                path=(
                    f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}"
                    f"/drafts/{quote(draft_id, safe='')}"
                ),
                body=params,
                method_options=options,
            )
        )

    def delete_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        draft_id: str,
        options: MethodOptions | None = None,
    ) -> None:
        self._client.request(
            RequestOptions(
                method="DELETE",
                path=(
                    f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}"
                    f"/drafts/{quote(draft_id, safe='')}"
                ),
                method_options=options,
            )
        )

    def send_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        draft_id: str,
        options: MethodOptions | None = None,
        *,
        expected_content_sha256: str | None = None,
    ) -> InboxReplyDraftSend:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=(
                    f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}"
                    f"/drafts/{quote(draft_id, safe='')}/send"
                ),
                body=(
                    {"expected_content_sha256": expected_content_sha256}
                    if expected_content_sha256 is not None
                    else None
                ),
                method_options=options,
            )
        )

    def reply_to_inbox_message(
        self,
        id: str,
        message_id: str,
        params: ReplyToMessageParams,
        options: MethodOptions | None = None,
    ) -> Message:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}/reply",
                body=params,
                method_options=options,
            )
        )

    def reply_to_inbox_thread(
        self,
        id: str,
        thread_id: str,
        params: ReplyToMessageParams,
        options: MethodOptions | None = None,
    ) -> Message:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}/reply",
                body=params,
                method_options=options,
            )
        )

    def download_inbox_attachment(
        self,
        id: str,
        params: DownloadInboxAttachmentParams,
        options: MethodOptions | None = None,
    ) -> bytes:
        return self._client.request_bytes(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/attachments",
                query={
                    "blob_id": params.get("blob_id"),
                    "message_id": params.get("message_id"),
                    "name": params.get("name"),
                },
                method_options=options,
            )
        )

    def update_inbox_message(
        self,
        id: str,
        message_id: str,
        params: UpdateInboxMessageParams,
        options: MethodOptions | None = None,
    ) -> InboxMessageAction:
        return self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}",
                body=params,
                method_options=options,
            )
        )

    def move_inbox_message(
        self,
        id: str,
        message_id: str,
        params: MoveInboxMessageParams,
        options: MethodOptions | None = None,
    ) -> InboxMessageAction:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}/move",
                body=params,
                method_options=options,
            )
        )

    def delete_inbox_message(self, id: str, message_id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}",
                method_options=options,
            )
        )

    def reset_password(
        self, id: str, params: ResetMailboxPasswordParams, options: MethodOptions | None = None
    ) -> Mailbox:
        return self._client.request(
            RequestOptions(
                method="PATCH", path=f"/mailboxes/{quote(id, safe='')}/password", body=params, method_options=options
            )
        )

    def list_app_passwords(self, id: str, options: MethodOptions | None = None) -> MailboxAppPasswordList:
        return self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/app-passwords", method_options=options)
        )

    def create_app_password(
        self,
        id: str,
        params: CreateMailboxAppPasswordParams,
        options: OneTimeSecretMethodOptions | None = None,
    ) -> CreatedMailboxAppPassword:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/app-passwords",
                body=params,
                method_options=options,
            )
        )

    def revoke_app_password(self, id: str, app_password_id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/app-passwords/{quote(app_password_id, safe='')}",
                method_options=options,
            )
        )

    def list_forwarding(self, id: str, options: MethodOptions | None = None) -> MailboxForwardingList:
        return self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/forwarding", method_options=options)
        )

    def create_forwarding(
        self, id: str, params: CreateMailboxForwardingParams, options: MethodOptions | None = None
    ) -> MailboxForwarding:
        return self._client.request(
            RequestOptions(
                method="POST", path=f"/mailboxes/{quote(id, safe='')}/forwarding", body=params, method_options=options
            )
        )

    def delete_forwarding(self, id: str, forwarding_id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/forwarding/{quote(forwarding_id, safe='')}",
                method_options=options,
            )
        )

    def update_auto_reply(
        self, id: str, params: UpdateAutoReplyParams, options: MethodOptions | None = None
    ) -> Mailbox:
        return self._client.request(
            RequestOptions(
                method="PATCH", path=f"/mailboxes/{quote(id, safe='')}/auto-reply", body=params, method_options=options
            )
        )

    def get_delivery_routing(
        self, id: str, options: MethodOptions | None = None
    ) -> MailboxDeliveryRouting:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/delivery-routing",
                method_options=options,
            )
        )

    def update_delivery_routing(
        self,
        id: str,
        params: UpdateMailboxDeliveryRoutingParams,
        options: MethodOptions | None = None,
    ) -> MailboxDeliveryRouting:
        return self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/mailboxes/{quote(id, safe='')}/delivery-routing",
                body=params,
                method_options=options,
            )
        )

    def create_import(
        self, id: str, params: CreateMailboxImportParams, options: MethodOptions | None = None
    ) -> MailboxImport:
        return self._client.request(
            RequestOptions(
                method="POST", path=f"/mailboxes/{quote(id, safe='')}/imports", body=params, method_options=options
            )
        )

    def list_imports(self, id: str, options: MethodOptions | None = None) -> MailboxImports:
        return self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/imports", method_options=options)
        )

    def get_import(self, id: str, import_id: str, options: MethodOptions | None = None) -> MailboxImport:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}",
                method_options=options,
            )
        )

    def cancel_import(self, id: str, import_id: str, options: MethodOptions | None = None) -> MailboxImport:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}/cancel",
                method_options=options,
            )
        )

    def resume_import(
        self, id: str, import_id: str, options: MethodOptions | None = None
    ) -> MailboxImport:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}/resume",
                method_options=options,
            )
        )

    def restore_import(
        self,
        id: str,
        import_id: str,
        params: RestoreMailboxImportParams,
        options: MethodOptions | None = None,
    ) -> MailboxImport:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}/restore",
                body=params,
                method_options=options,
            )
        )

    def undo_import(self, id: str, import_id: str, options: MethodOptions | None = None) -> MailboxImport:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}/undo",
                method_options=options,
            )
        )

    def create_import_upload(
        self, id: str, params: CreateImportUploadParams, options: MethodOptions | None = None
    ) -> ImportUpload:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/files",
                body=params,
                method_options=options,
            )
        )

    def complete_import_upload(
        self,
        id: str,
        file_id: str,
        params: CompleteImportUploadParams,
        options: MethodOptions | None = None,
    ) -> None:
        self._client.request(
            RequestOptions(
                method="POST",
                path=(f"/mailboxes/{quote(id, safe='')}/imports/files/{quote(file_id, safe='')}/complete"),
                body=params,
                method_options=options,
            )
        )

    def abort_import_upload(self, id: str, file_id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/imports/files/{quote(file_id, safe='')}",
                method_options=options,
            )
        )


class AsyncMailboxes:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def prepare_staged_attachment_upload(
        self,
        id: str,
        params: PrepareStagedAttachmentUploadParams,
        options: OneTimeSecretMethodOptions | None = None,
    ) -> StagedAttachmentUpload:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/staged-attachment-upload-tokens",
                body=params,
                method_options=options,
            )
        )

    async def stage_attachment(
        self,
        id: str,
        *,
        filename: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        options: MethodOptions | None = None,
    ) -> StagedAttachment:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/staged-attachments",
                query={"filename": filename},
                raw_body=data,
                content_type=content_type,
                method_options=options,
            )
        )

    async def inject_sandbox_inbound(
        self,
        id: str,
        params: InjectSandboxInboundParams | dict[str, object],
        options: MethodOptions | None = None,
    ) -> Message:
        body = dict(params)
        if "from_" in body:
            body["from"] = body.pop("from_")
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/sandbox/inbound",
                body=body,
                method_options=options,
            )
        )

    async def create(self, params: CreateMailboxParams, options: MethodOptions | None = None) -> Mailbox:
        return await self._client.request(
            RequestOptions(method="POST", path="/mailboxes", body=params, method_options=options)
        )

    async def list(
        self, params: ListMailboxesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/mailboxes",
                query={
                    "domain_id": params.get("domain_id") if params else None,
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, domain_id: str | None = None, limit: int | None = None) -> AsyncPage[Mailbox]:
        return AsyncPage(self._client, "/mailboxes", {"domain_id": domain_id, "limit": limit})

    async def get(self, id: str, options: MethodOptions | None = None) -> Mailbox:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}", method_options=options)
        )

    async def update(self, id: str, params: UpdateMailboxParams, options: MethodOptions | None = None) -> Mailbox:
        return await self._client.request(
            RequestOptions(method="PATCH", path=f"/mailboxes/{quote(id, safe='')}", body=params, method_options=options)
        )

    async def delete(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(method="DELETE", path=f"/mailboxes/{quote(id, safe='')}", method_options=options)
        )

    async def suspend(self, id: str, options: MethodOptions | None = None) -> Mailbox:
        return await self._client.request(
            RequestOptions(method="POST", path=f"/mailboxes/{quote(id, safe='')}/suspend", method_options=options)
        )

    async def resume(self, id: str, options: MethodOptions | None = None) -> Mailbox:
        return await self._client.request(
            RequestOptions(method="POST", path=f"/mailboxes/{quote(id, safe='')}/resume", method_options=options)
        )

    async def create_export(self, id: str, options: MethodOptions | None = None) -> MailboxExport:
        return await self._client.request(
            RequestOptions(method="POST", path=f"/mailboxes/{quote(id, safe='')}/exports", method_options=options)
        )

    async def get_export(self, id: str, export_id: str, options: MethodOptions | None = None) -> MailboxExport:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/exports/{quote(export_id, safe='')}",
                method_options=options,
            )
        )

    async def list_folders(self, id: str, options: MethodOptions | None = None) -> MailboxFolders:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/folders", method_options=options)
        )

    async def get_rules(self, id: str, options: MethodOptions | None = None) -> MailboxRules:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/rules", method_options=options)
        )

    async def update_rules(
        self, id: str, params: UpdateMailboxRulesParams, options: MethodOptions | None = None
    ) -> MailboxRules:
        return await self._client.request(
            RequestOptions(
                method="PUT", path=f"/mailboxes/{quote(id, safe='')}/rules", body=params, method_options=options
            )
        )

    async def create_folder(
        self, id: str, params: CreateMailboxFolderParams, options: MethodOptions | None = None
    ) -> MailboxFolder:
        return await self._client.request(
            RequestOptions(
                method="POST", path=f"/mailboxes/{quote(id, safe='')}/folders", body=params, method_options=options
            )
        )

    async def update_folder(
        self, id: str, folder_id: str, params: UpdateMailboxFolderParams, options: MethodOptions | None = None
    ) -> MailboxFolder:
        return await self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/mailboxes/{quote(id, safe='')}/folders/{quote(folder_id, safe='')}",
                body=params,
                method_options=options,
            )
        )

    async def delete_folder(self, id: str, folder_id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/folders/{quote(folder_id, safe='')}",
                method_options=options,
            )
        )

    async def list_identities(self, id: str, options: MethodOptions | None = None) -> MailboxIdentities:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/identities", method_options=options)
        )

    async def list_inbox_messages(
        self,
        id: str,
        params: ListInboxMessagesParams | None = None,
        options: MethodOptions | None = None,
    ) -> InboxMessages:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages",
                query={
                    "folder_id": params.get("folder_id") if params else None,
                    "folder_role": params.get("folder_role") if params else None,
                    "search_text": params.get("search_text") if params else None,
                    "from": params.get("from") if params else None,
                    "to": params.get("to") if params else None,
                    "subject": params.get("subject") if params else None,
                    "has_attachment": params.get("has_attachment") if params else None,
                    "cursor": params.get("cursor") if params else None,
                    "after": params.get("after") if params else None,
                    "before": params.get("before") if params else None,
                    "limit": params.get("limit") if params else None,
                    "has_keyword": params.get("has_keyword") if params else None,
                    "not_keyword": params.get("not_keyword") if params else None,
                },
                method_options=options,
            )
        )

    async def get_inbox_message(
        self, id: str, message_id: str, options: MethodOptions | None = None
    ) -> InboxFullMessage:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}",
                method_options=options,
            )
        )

    async def release_inbox_message_security(
        self,
        id: str,
        message_id: str,
        params: ReleaseInboxMessageSecurityParams,
        options: MethodOptions | None = None,
    ) -> InboxMessageSecurityReview:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}/security-review",
                body=params,
                method_options=options,
            )
        )

    async def list_inbox_threads(
        self,
        id: str,
        params: ListInboxThreadsParams | None = None,
        options: MethodOptions | None = None,
    ) -> InboxThreads:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads",
                query={
                    "attention_state": params.get("attention_state") if params else None,
                    "sort_by": params.get("sort_by") if params else None,
                    "order": params.get("order") if params else None,
                    "after": params.get("after") if params else None,
                    "before": params.get("before") if params else None,
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    async def get_inbox_thread(self, id: str, thread_id: str, options: MethodOptions | None = None) -> InboxThread:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}",
                method_options=options,
            )
        )

    async def update_inbox_thread_attention(
        self,
        id: str,
        thread_id: str,
        params: UpdateInboxThreadAttentionParams,
        options: MethodOptions | None = None,
    ) -> InboxThreadAttentionResult:
        return await self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}",
                body=params,
                method_options=options,
            )
        )

    async def create_inbox_draft(
        self,
        id: str,
        params: CreateInboxDraftParams,
        options: MethodOptions | None = None,
    ) -> InboxDraft:
        """Save a new message to the mailbox's Drafts folder. It is never sent by this call."""
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/drafts",
                body=params,
                method_options=options,
            )
        )

    async def create_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        params: CreateInboxReplyDraftParams,
        options: MethodOptions | None = None,
    ) -> InboxReplyDraftWrite:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}/drafts",
                body=params,
                method_options=options,
            )
        )

    async def list_inbox_reply_drafts(
        self, id: str, thread_id: str, options: MethodOptions | None = None
    ) -> InboxReplyDraftList:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}/drafts",
                method_options=options,
            )
        )

    async def get_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        draft_id: str,
        options: MethodOptions | None = None,
    ) -> InboxReplyDraft:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=(
                    f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}"
                    f"/drafts/{quote(draft_id, safe='')}"
                ),
                method_options=options,
            )
        )

    async def update_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        draft_id: str,
        params: UpdateInboxReplyDraftParams,
        options: MethodOptions | None = None,
    ) -> InboxReplyDraftWrite:
        return await self._client.request(
            RequestOptions(
                method="PATCH",
                path=(
                    f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}"
                    f"/drafts/{quote(draft_id, safe='')}"
                ),
                body=params,
                method_options=options,
            )
        )

    async def delete_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        draft_id: str,
        options: MethodOptions | None = None,
    ) -> None:
        await self._client.request(
            RequestOptions(
                method="DELETE",
                path=(
                    f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}"
                    f"/drafts/{quote(draft_id, safe='')}"
                ),
                method_options=options,
            )
        )

    async def send_inbox_reply_draft(
        self,
        id: str,
        thread_id: str,
        draft_id: str,
        options: MethodOptions | None = None,
        *,
        expected_content_sha256: str | None = None,
    ) -> InboxReplyDraftSend:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=(
                    f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}"
                    f"/drafts/{quote(draft_id, safe='')}/send"
                ),
                body=(
                    {"expected_content_sha256": expected_content_sha256}
                    if expected_content_sha256 is not None
                    else None
                ),
                method_options=options,
            )
        )

    async def reply_to_inbox_message(
        self,
        id: str,
        message_id: str,
        params: ReplyToMessageParams,
        options: MethodOptions | None = None,
    ) -> Message:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}/reply",
                body=params,
                method_options=options,
            )
        )

    async def reply_to_inbox_thread(
        self,
        id: str,
        thread_id: str,
        params: ReplyToMessageParams,
        options: MethodOptions | None = None,
    ) -> Message:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/threads/{quote(thread_id, safe='')}/reply",
                body=params,
                method_options=options,
            )
        )

    async def download_inbox_attachment(
        self,
        id: str,
        params: DownloadInboxAttachmentParams,
        options: MethodOptions | None = None,
    ) -> bytes:
        return await self._client.request_bytes(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/attachments",
                query={
                    "blob_id": params.get("blob_id"),
                    "message_id": params.get("message_id"),
                    "name": params.get("name"),
                },
                method_options=options,
            )
        )

    async def update_inbox_message(
        self,
        id: str,
        message_id: str,
        params: UpdateInboxMessageParams,
        options: MethodOptions | None = None,
    ) -> InboxMessageAction:
        return await self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}",
                body=params,
                method_options=options,
            )
        )

    async def move_inbox_message(
        self,
        id: str,
        message_id: str,
        params: MoveInboxMessageParams,
        options: MethodOptions | None = None,
    ) -> InboxMessageAction:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}/move",
                body=params,
                method_options=options,
            )
        )

    async def delete_inbox_message(self, id: str, message_id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/inbox/messages/{quote(message_id, safe='')}",
                method_options=options,
            )
        )

    async def reset_password(
        self, id: str, params: ResetMailboxPasswordParams, options: MethodOptions | None = None
    ) -> Mailbox:
        return await self._client.request(
            RequestOptions(
                method="PATCH", path=f"/mailboxes/{quote(id, safe='')}/password", body=params, method_options=options
            )
        )

    async def list_app_passwords(self, id: str, options: MethodOptions | None = None) -> MailboxAppPasswordList:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/app-passwords", method_options=options)
        )

    async def create_app_password(
        self,
        id: str,
        params: CreateMailboxAppPasswordParams,
        options: OneTimeSecretMethodOptions | None = None,
    ) -> CreatedMailboxAppPassword:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/app-passwords",
                body=params,
                method_options=options,
            )
        )

    async def revoke_app_password(self, id: str, app_password_id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/app-passwords/{quote(app_password_id, safe='')}",
                method_options=options,
            )
        )

    async def list_forwarding(self, id: str, options: MethodOptions | None = None) -> MailboxForwardingList:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/forwarding", method_options=options)
        )

    async def create_forwarding(
        self, id: str, params: CreateMailboxForwardingParams, options: MethodOptions | None = None
    ) -> MailboxForwarding:
        return await self._client.request(
            RequestOptions(
                method="POST", path=f"/mailboxes/{quote(id, safe='')}/forwarding", body=params, method_options=options
            )
        )

    async def delete_forwarding(self, id: str, forwarding_id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/forwarding/{quote(forwarding_id, safe='')}",
                method_options=options,
            )
        )

    async def update_auto_reply(
        self, id: str, params: UpdateAutoReplyParams, options: MethodOptions | None = None
    ) -> Mailbox:
        return await self._client.request(
            RequestOptions(
                method="PATCH", path=f"/mailboxes/{quote(id, safe='')}/auto-reply", body=params, method_options=options
            )
        )

    async def get_delivery_routing(
        self, id: str, options: MethodOptions | None = None
    ) -> MailboxDeliveryRouting:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/delivery-routing",
                method_options=options,
            )
        )

    async def update_delivery_routing(
        self,
        id: str,
        params: UpdateMailboxDeliveryRoutingParams,
        options: MethodOptions | None = None,
    ) -> MailboxDeliveryRouting:
        return await self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/mailboxes/{quote(id, safe='')}/delivery-routing",
                body=params,
                method_options=options,
            )
        )

    async def create_import(
        self, id: str, params: CreateMailboxImportParams, options: MethodOptions | None = None
    ) -> MailboxImport:
        return await self._client.request(
            RequestOptions(
                method="POST", path=f"/mailboxes/{quote(id, safe='')}/imports", body=params, method_options=options
            )
        )

    async def list_imports(self, id: str, options: MethodOptions | None = None) -> MailboxImports:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/mailboxes/{quote(id, safe='')}/imports", method_options=options)
        )

    async def get_import(self, id: str, import_id: str, options: MethodOptions | None = None) -> MailboxImport:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}",
                method_options=options,
            )
        )

    async def cancel_import(self, id: str, import_id: str, options: MethodOptions | None = None) -> MailboxImport:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}/cancel",
                method_options=options,
            )
        )

    async def resume_import(
        self, id: str, import_id: str, options: MethodOptions | None = None
    ) -> MailboxImport:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}/resume",
                method_options=options,
            )
        )

    async def restore_import(
        self,
        id: str,
        import_id: str,
        params: RestoreMailboxImportParams,
        options: MethodOptions | None = None,
    ) -> MailboxImport:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}/restore",
                body=params,
                method_options=options,
            )
        )

    async def undo_import(self, id: str, import_id: str, options: MethodOptions | None = None) -> MailboxImport:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/{quote(import_id, safe='')}/undo",
                method_options=options,
            )
        )

    async def create_import_upload(
        self, id: str, params: CreateImportUploadParams, options: MethodOptions | None = None
    ) -> ImportUpload:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/mailboxes/{quote(id, safe='')}/imports/files",
                body=params,
                method_options=options,
            )
        )

    async def complete_import_upload(
        self,
        id: str,
        file_id: str,
        params: CompleteImportUploadParams,
        options: MethodOptions | None = None,
    ) -> None:
        await self._client.request(
            RequestOptions(
                method="POST",
                path=(f"/mailboxes/{quote(id, safe='')}/imports/files/{quote(file_id, safe='')}/complete"),
                body=params,
                method_options=options,
            )
        )

    async def abort_import_upload(self, id: str, file_id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/mailboxes/{quote(id, safe='')}/imports/files/{quote(file_id, safe='')}",
                method_options=options,
            )
        )
