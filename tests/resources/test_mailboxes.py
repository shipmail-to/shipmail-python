from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_mailbox = {
    "object": "mailbox",
    "id": "mbx_123",
    "domain_id": "dom_456",
    "address": "hello@example.com",
    "display_name": "Hello",
    "suspended_at": None,
    "suspension_reasons": [],
    "auto_reply": {
        "enabled": False,
        "subject": None,
        "body": None,
        "from_date": None,
        "to_date": None,
    },
    "agent_security_hold": False,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

mock_mailbox_export = {
    "object": "mailbox_export",
    "id": "mbexp_0123456789abcdefghjkmnpq",
    "mailbox_id": "mbx_123",
    "status": "completed",
    "format": "zip",
    "format_version": 1,
    "file_size": 4096,
    "message_count": 12,
    "folder_count": 4,
    "error_code": None,
    "download_url": "https://download.test/export.zip",
    "download_url_expires_at": "2026-07-13T12:05:00.000Z",
    "expires_at": "2026-07-20T12:00:00.000Z",
    "created_at": "2026-07-13T12:00:00.000Z",
    "started_at": "2026-07-13T12:00:01.000Z",
    "completed_at": "2026-07-13T12:00:02.000Z",
}


class TestPrepareStagedAttachmentUpload:
    def test_creates_one_time_upload_without_idempotency(self) -> None:
        response = {
            "object": "staged_attachment_upload",
            "mailbox_id": "mbx_123",
            "filename": "invoice.pdf",
            "content_type": "application/pdf",
            "size": 4,
            "sha256": "a" * 64,
            "upload_url": "https://shipmail.to/api/v1/staged-attachment-uploads/token",
            "expires_at": "2026-07-24T12:05:00.000Z",
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/staged-attachment-upload-tokens"
            assert "idempotency-key" not in request.headers
            assert json.loads(request.content) == {
                "filename": "invoice.pdf",
                "content_type": "application/pdf",
                "size": 4,
                "sha256": "a" * 64,
            }
            return json_response(response, 201)

        result = make_client(handler).mailboxes.prepare_staged_attachment_upload(
            "mbx_123",
            {
                "filename": "invoice.pdf",
                "content_type": "application/pdf",
                "size": 4,
                "sha256": "a" * 64,
            },
        )
        assert result == response

    @pytest.mark.asyncio
    async def test_creates_one_time_upload_async(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/mailboxes/mbx_123/staged-attachment-upload-tokens"
            return json_response(
                {
                    "object": "staged_attachment_upload",
                    "mailbox_id": "mbx_123",
                    "filename": "invoice.pdf",
                    "content_type": "application/pdf",
                    "size": 4,
                    "sha256": "a" * 64,
                    "upload_url": "https://shipmail.to/api/v1/staged-attachment-uploads/token",
                    "expires_at": "2026-07-24T12:05:00.000Z",
                },
                201,
            )

        result = await make_async_client(handler).mailboxes.prepare_staged_attachment_upload(
            "mbx_123",
            {
                "filename": "invoice.pdf",
                "content_type": "application/pdf",
                "size": 4,
                "sha256": "a" * 64,
            },
        )
        assert result["object"] == "staged_attachment_upload"


class TestStageAttachment:
    def test_uploads_raw_bytes(self) -> None:
        response = {
            "object": "staged_attachment",
            "id": "sat_123",
            "mailbox_id": "mbx_123",
            "filename": "invoice.pdf",
            "content_type": "application/pdf",
            "size": 4,
            "sha256": "a" * 64,
            "expires_at": "2026-07-25T12:00:00.000Z",
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/staged-attachments"
            assert request.url.params["filename"] == "invoice.pdf"
            assert request.headers["content-type"] == "application/pdf"
            assert request.content == b"%PDF"
            return json_response(response, 201)

        result = make_client(handler).mailboxes.stage_attachment(
            "mbx_123",
            filename="invoice.pdf",
            content_type="application/pdf",
            data=b"%PDF",
        )
        assert result == response


mock_forwarding = {
    "object": "mailbox_forwarding",
    "id": "fwd_0123456789abcdefghjkmnpq",
    "mailbox_id": "mbx_123",
    "destination": "owner@example.net",
    "sender": "newsletter@example.com",
    "recipient": "nabeel@example.com",
    "status": "pending",
    "verification_sent_at": "2026-07-13T12:00:00Z",
    "verified_at": None,
    "created_at": "2026-07-13T12:00:00Z",
    "updated_at": "2026-07-13T12:00:00Z",
}

mock_forwarding_list = {
    "object": "mailbox_forwarding_list",
    "mailbox_id": "mbx_123",
    "data": [mock_forwarding],
}

mock_folder = {
    "object": "mailbox_folder",
    "id": "fld_123",
    "name": "VIP",
    "parent_id": None,
    "role": None,
    "kind": "custom",
    "total_emails": 0,
    "unread_emails": 0,
    "unread_threads": 0,
    "sort_order": 0,
}

mock_folders = {
    "object": "mailbox_folders",
    "mailbox_id": "mbx_123",
    "address": "hello@example.com",
    "data": [mock_folder],
}

mock_rules = {
    "object": "mailbox_rules",
    "mailbox_id": "mbx_123",
    "address": "hello@example.com",
    "rules": [
        {
            "id": "rule_123",
            "name": "Flag invoices",
            "enabled": True,
            "position": 0,
            "match_mode": "all",
            "stop": False,
            "conditions": [{"type": "subject_contains", "value": "invoice"}],
            "actions": [{"type": "star"}],
        }
    ],
    "folders": [
        {
            "id": "fld_123",
            "name": "VIP",
            "parent_id": None,
            "role": None,
            "kind": "custom",
        }
    ],
}

mock_identities = {
    "object": "mailbox_identities",
    "mailbox_id": "mbx_123",
    "address": "hello@example.com",
    "data": [
        {
            "object": "mailbox_identity",
            "id": "ident_123",
            "name": "Hello",
            "email": "hello@example.com",
        },
    ],
}

mock_inbox_messages = {
    "object": "inbox_messages",
    "mailbox_id": "mbx_123",
    "address": "hello@example.com",
    "junk_total": None,
    "data": [
        {
            "object": "inbox_message_full",
            "id": "eml_123",
            "thread_id": "thr_123",
            "conversation_id": "thd_123",
            "mailbox_id": "mbx_123",
            "address": "hello@example.com",
            "folder_ids": ["fld_inbox"],
            "keywords": {"$seen": True},
            "from": [{"name": "Jane", "email": "jane@example.com"}],
            "to": [{"name": None, "email": "hello@example.com"}],
            "cc": None,
            "reply_to": None,
            "message_id": ["msg-1@example.com"],
            "in_reply_to": None,
            "references": None,
            "subject": "Hello",
            "received_at": "2026-05-13T12:00:00Z",
            "preview": "Accept your Linear invite",
            "has_attachment": True,
            "size": 456,
            "body_values": {
                "body_1": {
                    "value": "Accept your Linear invite: https://linear.app/invite/example",
                    "is_encoding_problem": False,
                }
            },
            "text_body": [{"part_id": "body_1", "type": "text/plain"}],
            "html_body": [],
            "attachments": [
                {
                    "part_id": "att_1",
                    "blob_id": "blob/123",
                    "name": "invite.ics",
                    "content_type": "text/calendar",
                    "size": 1024,
                    "download_path": "/mailboxes/mbx_123/inbox/attachments?message_id=eml_123&blob_id=blob%2F123&name=invite.ics",
                }
            ],
            "authentication_results": {
                "spf": "pass",
                "dkim": "pass",
                "dmarc": "pass",
                "spam": {"isSpam": False, "scoreMilli": -1200},
                "raw": {
                    "authenticationResults": "mx.example; spf=pass; dkim=pass; dmarc=pass",
                    "receivedSpf": "pass",
                    "spamStatus": "No, score=-1.2",
                },
            },
            "security": {
                "status": "flagged",
                "risk_codes": ["instruction_override"],
                "scanner": "pattern_v1",
                "content_sha256": "a" * 64,
                "review": None,
            },
            "reply_text": "Accept your Linear invite",
        }
    ],
    "pagination": {"limit": 10, "total": 1, "has_more": False, "next_cursor": None},
}

mock_inbox_thread = {
    "object": "inbox_thread",
    "mailbox_id": "mbx_123",
    "address": "hello@example.com",
    "thread_id": "thr_123",
    "conversation_id": "thd_123",
    "version": 7,
    "data": [
        {
            "object": "inbox_message_full",
            "id": "eml_123",
            "thread_id": "thr_123",
            "conversation_id": "thd_123",
            "mailbox_id": "mbx_123",
            "address": "hello@example.com",
            "folder_ids": ["fld_inbox"],
            "keywords": {},
            "from": [{"name": "Jane", "email": "jane@example.com"}],
            "to": [{"name": None, "email": "hello@example.com"}],
            "cc": None,
            "reply_to": None,
            "message_id": ["msg-1@example.com"],
            "in_reply_to": None,
            "references": None,
            "subject": "Hello",
            "received_at": "2026-05-13T12:00:00Z",
            "preview": "Hi",
            "has_attachment": True,
            "size": 456,
            "body_values": {"body_1": {"value": "Hi", "is_encoding_problem": False}},
            "text_body": [{"part_id": "body_1", "type": "text/plain"}],
            "html_body": [],
            "attachments": [
                {
                    "part_id": "att_1",
                    "blob_id": "blob/123",
                    "name": "invoice.pdf",
                    "content_type": "application/pdf",
                    "size": 1024,
                    "download_path": "/mailboxes/mbx_123/inbox/attachments?message_id=eml_123&blob_id=blob%2F123&name=invoice.pdf",
                }
            ],
            "authentication_results": {
                "spf": "pass",
                "dkim": "pass",
                "dmarc": "pass",
                "spam": {"isSpam": False, "scoreMilli": -1200},
                "raw": {
                    "authenticationResults": "mx.example; spf=pass; dkim=pass; dmarc=pass",
                    "receivedSpf": "pass",
                    "spamStatus": "No, score=-1.2",
                },
            },
            "security": {
                "status": "not_flagged",
                "risk_codes": [],
                "scanner": "pattern_v1",
                "content_sha256": "b" * 64,
                "review": None,
            },
            "reply_text": "Hi",
        }
    ],
}

mock_inbox_draft = {
    "object": "inbox_draft",
    "id": "eml_draft",
    "mailbox_id": "mbx_123",
    "from": {"address": "hello@example.com", "name": "Hello"},
    "to": [{"address": "jane@example.com", "name": "Jane"}],
    "cc": [{"address": "ops@example.com", "name": None}],
    "bcc": [],
    "subject": "Kickoff",
    "removed_formatting": [],
    "created_at": "2026-09-24T00:00:00.000Z",
}

mock_inbox_reply_draft = {
    "object": "inbox_reply_draft",
    "id": "drf_123",
    "mailbox_id": "mbx_123",
    "thread_id": "thr_123",
    "conversation_id": "thd_123",
    "based_on_message_id": "msg_123",
    "expected_version": 7,
    "reply_mode": "reply",
    "status": "draft",
    "to": [{"address": "jane@example.com", "name": "Jane"}],
    "cc": [],
    "subject": "Re: Kickoff",
    "html": "<p>Thanks.</p>",
    "text": "Thanks.",
    "content_sha256": "a" * 64,
    "sent_message_id": None,
    "created_at": "2026-10-16T00:00:00.000Z",
    "updated_at": "2026-10-16T00:01:00.000Z",
    "sent_at": None,
}

mock_inbox_message_action = {
    "object": "inbox_message_action",
    "mailbox_id": "mbx_123",
    "address": "hello@example.com",
    "message_id": "eml_123",
    "ok": True,
    "folder_ids": ["fld_inbox"],
    "keywords": {"$seen": True},
}

mock_import = {
    "object": "import",
    "id": "imp_abc123",
    "mailbox_id": "mbx_123",
    "kind": "imap",
    "provider": "gmail",
    "source_address": "old@gmail.com",
    "status": "running",
    "status_detail": None,
    "error": None,
    "resume_at": None,
    "counts": {
        "found": 100,
        "imported": 42,
        "undone": 0,
        "duplicates_skipped": 3,
        "oversize_skipped": 1,
        "failed": 0,
        "contacts_imported": 7,
    },
    "bytes": {"total": 1048576, "imported": 524288},
    "created_at": "2026-06-12T00:00:00Z",
    "started_at": "2026-06-12T00:00:05Z",
    "completed_at": None,
}

mock_import_with_folders = {
    **mock_import,
    "folders": [
        {
            "source_folder": "INBOX",
            "target_folder": "Inbox",
            "role": "inbox",
            "state": "importing",
            "found": 100,
            "imported": 42,
            "duplicates": 3,
            "oversize": 1,
            "failed": 0,
        }
    ],
}

mock_imports = {
    "object": "imports",
    "mailbox_id": "mbx_123",
    "data": [mock_import],
}

mock_import_upload = {
    "object": "import_upload",
    "file_id": "impf_abc123",
    "part_size_bytes": 33554432,
    "parts": [{"part_number": 1, "upload_url": "https://uploads.example.com/impf_abc123?part=1"}],
    "expires_in_seconds": 518400,
}


class TestCreate:
    def test_sends_post_mailboxes_with_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes"
            body = json.loads(request.content)
            assert body == {
                "domain_id": "dom_456",
                "address": "hello@example.com",
                "password": "StrongPass123",
                "display_name": "Hello",
            }
            return json_response(mock_mailbox)

        client = make_client(handler)
        mailbox = client.mailboxes.create(
            {
                "domain_id": "dom_456",
                "address": "hello@example.com",
                "password": "StrongPass123",
                "display_name": "Hello",
            }
        )
        assert mailbox["id"] == "mbx_123"
        assert mailbox["address"] == "hello@example.com"

    def test_creates_mailbox_without_display_name(self) -> None:
        without_name = {**mock_mailbox, "display_name": None}

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {
                "domain_id": "dom_456",
                "address": "hello@example.com",
                "password": "StrongPass123",
            }
            return json_response(without_name)

        client = make_client(handler)
        mailbox = client.mailboxes.create(
            {
                "domain_id": "dom_456",
                "address": "hello@example.com",
                "password": "StrongPass123",
            }
        )
        assert mailbox["display_name"] is None

    def test_requests_server_generated_primary_password(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {
                "domain_id": "dom_456",
                "address": "support",
                "generate_password": True,
            }
            return json_response(mock_mailbox)

        client = make_client(handler)
        client.mailboxes.create(
            {
                "domain_id": "dom_456",
                "address": "support",
                "generate_password": True,
            }
        )


class TestInjectSandboxInbound:
    def test_sends_fake_inbound_to_sandbox_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/sandbox/inbound"
            assert json.loads(request.content) == {
                "from": "customer@example.com",
                "subject": "Sandbox reply",
                "text": "Looks good",
            }
            return json_response({"object": "message", "id": "msg_test", "mode": "test"}, status_code=201)

        client = make_client(handler)
        message = client.mailboxes.inject_sandbox_inbound(
            "mbx_123",
            {"from_": "customer@example.com", "subject": "Sandbox reply", "text": "Looks good"},
        )

        assert message["mode"] == "test"


class TestList:
    def test_sends_get_mailboxes(self) -> None:
        response = {
            "data": [mock_mailbox],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes"
            return json_response(response)

        client = make_client(handler)
        result = client.mailboxes.list()
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == "mbx_123"

    def test_sends_domain_id_filter(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url.params.get("domain_id")) == "dom_456"
            return json_response(response)

        client = make_client(handler)
        client.mailboxes.list({"domain_id": "dom_456"})

    def test_sends_cursor_and_limit(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url.params.get("cursor")) == "cur_xyz"
            assert str(request.url.params.get("limit")) == "10"
            return json_response(response)

        client = make_client(handler)
        client.mailboxes.list({"cursor": "cur_xyz", "limit": 10})


class TestGet:
    def test_sends_get_mailboxes_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123"
            return json_response(mock_mailbox)

        client = make_client(handler)
        mailbox = client.mailboxes.get("mbx_123")
        assert mailbox["id"] == "mbx_123"
        assert mailbox["address"] == "hello@example.com"


class TestUpdate:
    def test_sends_patch_mailboxes_id_with_body(self) -> None:
        updated = {
            **mock_mailbox,
            "display_name": "Updated Name",
            "agent_security_hold": True,
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/mailboxes/mbx_123"
            body = json.loads(request.content)
            assert body == {
                "display_name": "Updated Name",
                "agent_security_hold": True,
            }
            return json_response(updated)

        client = make_client(handler)
        mailbox = client.mailboxes.update(
            "mbx_123",
            {"display_name": "Updated Name", "agent_security_hold": True},
        )
        assert mailbox["display_name"] == "Updated Name"
        assert mailbox["agent_security_hold"] is True

    def test_sends_null_to_clear_display_name(self) -> None:
        updated = {**mock_mailbox, "display_name": None}

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"display_name": None}
            return json_response(updated)

        client = make_client(handler)
        mailbox = client.mailboxes.update("mbx_123", {"display_name": None})
        assert mailbox["display_name"] is None


class TestDelete:
    def test_sends_delete_mailboxes_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/mailboxes/mbx_123"
            return httpx.Response(204)

        client = make_client(handler)
        result = client.mailboxes.delete("mbx_123")
        assert result is None


class TestSuspension:
    def test_suspends_and_resumes_mailbox(self) -> None:
        paths: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            paths.append(request.url.path)
            return json_response(mock_mailbox)

        client = make_client(handler)
        client.mailboxes.suspend("mbx_123")
        client.mailboxes.resume("mbx_123")

        assert paths == ["/v1/mailboxes/mbx_123/suspend", "/v1/mailboxes/mbx_123/resume"]


class TestResetPassword:
    def test_sends_patch_mailboxes_id_password(self) -> None:
        updated = {**mock_mailbox, "updated_at": "2026-05-13T12:00:00Z"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/mailboxes/mbx_123/password"
            body = json.loads(request.content)
            assert body == {"password": "NewPassword1"}
            return json_response(updated)

        client = make_client(handler)
        mailbox = client.mailboxes.reset_password("mbx_123", {"password": "NewPassword1"})
        assert mailbox["updated_at"] == "2026-05-13T12:00:00Z"


class TestForwarding:
    def test_lists_mailbox_forwarding(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/forwarding"
            return json_response(mock_forwarding_list)

        client = make_client(handler)
        forwarding = client.mailboxes.list_forwarding("mbx_123")
        assert forwarding["data"][0]["destination"] == "owner@example.net"
        assert forwarding["data"][0]["sender"] == "newsletter@example.com"
        assert forwarding["data"][0]["recipient"] == "nabeel@example.com"

    def test_creates_mailbox_forwarding(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/forwarding"
            assert json.loads(request.content) == {
                "destination": "owner@example.net",
                "sender": "newsletter@example.com",
                "recipient": "nabeel@example.com",
            }
            return json_response(mock_forwarding)

        client = make_client(handler)
        forwarding = client.mailboxes.create_forwarding(
            "mbx_123",
            {
                "destination": "owner@example.net",
                "sender": "newsletter@example.com",
                "recipient": "nabeel@example.com",
            },
        )
        assert forwarding["status"] == "pending"

    def test_deletes_mailbox_forwarding(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == ("/v1/mailboxes/mbx_123/forwarding/fwd_0123456789abcdefghjkmnpq")
            return httpx.Response(204)

        client = make_client(handler)
        result = client.mailboxes.delete_forwarding("mbx_123", "fwd_0123456789abcdefghjkmnpq")
        assert result is None


class TestFolders:
    def test_sends_get_mailboxes_id_folders(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/folders"
            return json_response(mock_folders)

        client = make_client(handler)
        folders = client.mailboxes.list_folders("mbx_123")
        assert folders["data"][0]["id"] == "fld_123"

    def test_sends_post_mailboxes_id_folders(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/folders"
            body = json.loads(request.content)
            assert body == {"name": "VIP", "parent_id": None}
            return json_response(mock_folder, status_code=201)

        client = make_client(handler)
        folder = client.mailboxes.create_folder("mbx_123", {"name": "VIP", "parent_id": None})
        assert folder["name"] == "VIP"

    def test_sends_patch_mailboxes_id_folders_folder_id(self) -> None:
        renamed = {**mock_folder, "name": "VIP Clients"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/mailboxes/mbx_123/folders/fld_123"
            body = json.loads(request.content)
            assert body == {"name": "VIP Clients"}
            return json_response(renamed)

        client = make_client(handler)
        folder = client.mailboxes.update_folder("mbx_123", "fld_123", {"name": "VIP Clients"})
        assert folder["name"] == "VIP Clients"

    def test_sends_delete_mailboxes_id_folders_folder_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/mailboxes/mbx_123/folders/fld_123"
            return httpx.Response(204)

        client = make_client(handler)
        result = client.mailboxes.delete_folder("mbx_123", "fld_123")
        assert result is None


class TestRules:
    def test_gets_mailbox_rules(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/rules"
            return json_response(mock_rules)

        rules = make_client(handler).mailboxes.get_rules("mbx_123")
        assert rules["rules"][0]["name"] == "Flag invoices"

    def test_replaces_mailbox_rules(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PUT"
            assert request.url.path == "/v1/mailboxes/mbx_123/rules"
            assert json.loads(request.content) == {"rules": mock_rules["rules"]}
            return json_response(mock_rules)

        rules = make_client(handler).mailboxes.update_rules("mbx_123", {"rules": mock_rules["rules"]})
        assert rules["rules"][0]["id"] == "rule_123"

    @pytest.mark.asyncio
    async def test_replaces_mailbox_rules_async(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PUT"
            assert request.url.path == "/v1/mailboxes/mbx_123/rules"
            return json_response(mock_rules)

        rules = await make_async_client(handler).mailboxes.update_rules("mbx_123", {"rules": mock_rules["rules"]})
        assert rules["rules"][0]["id"] == "rule_123"


class TestIdentities:
    def test_sends_get_mailboxes_id_identities(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/identities"
            return json_response(mock_identities)

        client = make_client(handler)
        identities = client.mailboxes.list_identities("mbx_123")
        assert identities["data"][0]["email"] == "hello@example.com"


class TestInbox:
    def test_releases_exact_security_review_snapshot(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/messages/eml_123/security-review"
            assert json.loads(request.content) == {
                "decision": "release",
                "reason": "Known invoice workflow",
                "expected_content_sha256": "a" * 64,
            }
            return json_response(
                {
                    "object": "inbox_message_security_review",
                    "mailbox_id": "mbx_123",
                    "message_id": "eml_123",
                    "security": {
                        "status": "flagged",
                        "risk_codes": ["instruction_override"],
                        "scanner": "pattern_v1",
                        "content_sha256": "a" * 64,
                        "review": {
                            "decision": "released",
                            "released_at": "2026-10-23T12:00:00.000Z",
                            "released_by": "api_key",
                        },
                    },
                }
            )

        result = make_client(handler).mailboxes.release_inbox_message_security(
            "mbx_123",
            "eml_123",
            {
                "decision": "release",
                "reason": "Known invoice workflow",
                "expected_content_sha256": "a" * 64,
            },
        )
        review = result["security"]["review"]
        assert review is not None
        assert review["released_by"] == "api_key"

    @pytest.mark.asyncio
    async def test_releases_exact_security_review_snapshot_async(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            return json_response(
                {
                    "object": "inbox_message_security_review",
                    "mailbox_id": "mbx_123",
                    "message_id": "eml_123",
                    "security": {
                        "status": "not_scanned",
                        "risk_codes": [],
                        "scanner": "pattern_v1",
                        "content_sha256": "a" * 64,
                        "review": None,
                    },
                }
            )

        result = await make_async_client(handler).mailboxes.release_inbox_message_security(
            "mbx_123",
            "eml_123",
            {
                "decision": "release",
                "reason": "Manual verification",
                "expected_content_sha256": "a" * 64,
            },
        )
        assert result["message_id"] == "eml_123"

    def test_sends_get_mailboxes_id_inbox_messages(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/messages"
            assert str(request.url.params.get("folder_role")) == "inbox"
            assert str(request.url.params.get("cursor")) == "cursor_5"
            assert str(request.url.params.get("after")) == "2025-07-20T00:00:00.000Z"
            assert str(request.url.params.get("before")) == "2026-07-20T00:00:00.000Z"
            assert str(request.url.params.get("limit")) == "10"
            assert str(request.url.params.get("has_keyword")) == "$seen"
            return json_response(mock_inbox_messages)

        client = make_client(handler)
        messages = client.mailboxes.list_inbox_messages(
            "mbx_123",
            {
                "folder_role": "inbox",
                "cursor": "cursor_5",
                "after": "2025-07-20T00:00:00.000Z",
                "before": "2026-07-20T00:00:00.000Z",
                "limit": 10,
                "has_keyword": "$seen",
            },
        )
        assert messages["data"][0]["id"] == "eml_123"
        assert "linear.app/invite" in messages["data"][0]["body_values"]["body_1"]["value"]
        assert messages["data"][0]["authentication_results"]["dmarc"] == "pass"

    def test_sends_inbox_listing_filters(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            params = request.url.params
            assert params.get("from") == "jane@example.com"
            assert params.get("to") == "billing"
            assert params.get("subject") == "Invoice"
            assert params.get("has_attachment") == "false"
            return json_response(mock_inbox_messages)

        client = make_client(handler)
        messages = client.mailboxes.list_inbox_messages(
            "mbx_123",
            {"from": "jane@example.com", "to": "billing", "subject": "Invoice", "has_attachment": False},
        )
        assert messages["data"][0]["id"] == "eml_123"

    @pytest.mark.asyncio
    async def test_sends_inbox_listing_filters_async(self) -> None:
        paths: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            paths.append(str(request.url))
            return json_response(mock_inbox_messages)

        client = make_async_client(handler)
        await client.mailboxes.list_inbox_messages("mbx_123", {"subject": "Invoice", "has_attachment": True})
        assert paths == [
            "https://api.test.com/v1/mailboxes/mbx_123/inbox/messages?subject=Invoice&has_attachment=true",
        ]

    def test_gets_exact_message_and_uses_safe_reply_workflow(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.raw_path.decode()))
            if request.url.path.endswith("/messages/eml_123"):
                return json_response(mock_inbox_messages["data"][0])
            if request.method == "GET":
                assert request.url.params.get("attention_state") == "needs_reply"
                assert request.url.params.get("cursor") == "opaque_cursor"
                return json_response(
                    {
                        "object": "inbox_threads",
                        "mailbox_id": "mbx_123",
                        "data": [],
                        "summary": {
                            "needs_reply": 0,
                            "waiting_on_them": 0,
                            "done": 0,
                            "follow_up_due": 0,
                            "delivery_failed": 0,
                            "no_action": 0,
                        },
                        "pagination": {
                            "limit": 25,
                            "has_more": False,
                            "next_cursor": None,
                            "snapshot_at": "2026-07-20T00:00:00.000Z",
                        },
                    }
                )
            if request.url.path.endswith("/send"):
                assert json.loads(request.content) == {"expected_content_sha256": "a" * 64}
                return json_response(
                    {
                        "object": "inbox_reply_draft_send",
                        "draft_id": "drf_123",
                        "status": "sent",
                        "message": {"object": "message", "id": "msg_sent"},
                    }
                )
            body = json.loads(request.content)
            if request.method == "PATCH":
                assert body == {"done": True, "expected_version": 7}
                return json_response(
                    {
                        "object": "inbox_thread_attention",
                        "id": "thd_123",
                        "thread_id": "thr_123",
                        "conversation_id": "thd_123",
                        "attention_state": "done",
                        "version": 8,
                        "attention_since": None,
                        "done_at": "2026-07-20T00:00:00.000Z",
                        "follow_up_at": None,
                    }
                )
            if request.url.path.endswith("/drafts"):
                assert body == {
                    "text": "Thanks for the note.",
                    "expected_version": 7,
                    "reply_mode": "reply_all",
                }
                return json_response(
                    {
                        "object": "inbox_reply_draft",
                        "id": "drf_123",
                        "mailbox_id": "mbx_123",
                        "thread_id": "thr_123",
                        "conversation_id": "thd_123",
                        "based_on_message_id": "msg_123",
                        "expected_version": 7,
                        "reply_mode": "reply_all",
                        "status": "draft",
                        "to": [{"address": "jane@example.com", "name": "Jane"}],
                        "cc": [],
                        "created_at": "2026-07-20T00:00:00.000Z",
                    }
                )
            raise AssertionError(f"unexpected request: {request.method} {request.url}")

        client = make_client(handler)
        exact = client.mailboxes.get_inbox_message("mbx_123", "eml_123")
        queue = client.mailboxes.list_inbox_threads(
            "mbx_123", {"attention_state": "needs_reply", "cursor": "opaque_cursor"}
        )
        state = client.mailboxes.update_inbox_thread_attention(
            "mbx_123",
            "thr_123",
            {"done": True, "expected_version": 7},
        )
        draft = client.mailboxes.create_inbox_reply_draft(
            "mbx_123",
            "thr_123",
            {
                "text": "Thanks for the note.",
                "expected_version": 7,
                "reply_mode": "reply_all",
            },
        )
        sent = client.mailboxes.send_inbox_reply_draft(
            "mbx_123",
            "thr_123",
            "drf_123",
            expected_content_sha256="a" * 64,
        )

        assert exact["id"] == "eml_123"
        assert exact["authentication_results"]["spam"]["scoreMilli"] == -1200
        assert queue["object"] == "inbox_threads"
        assert state["version"] == 8
        assert draft["status"] == "draft"
        assert sent["status"] == "sent"
        assert calls == [
            ("GET", "/v1/mailboxes/mbx_123/inbox/messages/eml_123"),
            (
                "GET",
                "/v1/mailboxes/mbx_123/inbox/threads?attention_state=needs_reply&cursor=opaque_cursor",
            ),
            ("PATCH", "/v1/mailboxes/mbx_123/inbox/threads/thr_123"),
            ("POST", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts"),
            ("POST", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts/drf_123/send"),
        ]

    def test_lists_reads_updates_and_deletes_reply_drafts(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.path))
            if request.method == "PATCH":
                assert json.loads(request.content) == {"html": "<p>Thanks.</p><table></table>"}
                return json_response({**mock_inbox_reply_draft, "removed_formatting": ["table"]})
            if request.method == "DELETE":
                return httpx.Response(204)
            if request.url.path.endswith("/drafts"):
                return json_response({"object": "list", "data": [mock_inbox_reply_draft]})
            return json_response(mock_inbox_reply_draft)

        client = make_client(handler)
        drafts = client.mailboxes.list_inbox_reply_drafts("mbx_123", "thr_123")
        draft = client.mailboxes.get_inbox_reply_draft("mbx_123", "thr_123", "drf_123")
        updated = client.mailboxes.update_inbox_reply_draft(
            "mbx_123", "thr_123", "drf_123", {"html": "<p>Thanks.</p><table></table>"}
        )
        deleted = client.mailboxes.delete_inbox_reply_draft("mbx_123", "thr_123", "drf_123")

        assert drafts["data"][0]["html"] == "<p>Thanks.</p>"
        assert draft["updated_at"] == "2026-10-16T00:01:00.000Z"
        assert updated["removed_formatting"] == ["table"]
        assert deleted is None
        assert calls == [
            ("GET", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts"),
            ("GET", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts/drf_123"),
            ("PATCH", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts/drf_123"),
            ("DELETE", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts/drf_123"),
        ]

    @pytest.mark.asyncio
    async def test_lists_reads_updates_and_deletes_reply_drafts_async(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.path))
            if request.method == "PATCH":
                assert json.loads(request.content) == {"text": "Thanks."}
                return json_response({**mock_inbox_reply_draft, "removed_formatting": []})
            if request.method == "DELETE":
                return httpx.Response(204)
            if request.url.path.endswith("/drafts"):
                return json_response({"object": "list", "data": [mock_inbox_reply_draft]})
            return json_response(mock_inbox_reply_draft)

        client = make_async_client(handler)
        drafts = await client.mailboxes.list_inbox_reply_drafts("mbx_123", "thr_123")
        draft = await client.mailboxes.get_inbox_reply_draft("mbx_123", "thr_123", "drf_123")
        updated = await client.mailboxes.update_inbox_reply_draft(
            "mbx_123", "thr_123", "drf_123", {"text": "Thanks."}
        )
        deleted = await client.mailboxes.delete_inbox_reply_draft("mbx_123", "thr_123", "drf_123")

        assert drafts["object"] == "list"
        assert draft["id"] == "drf_123"
        assert updated["removed_formatting"] == []
        assert deleted is None
        assert calls == [
            ("GET", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts"),
            ("GET", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts/drf_123"),
            ("PATCH", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts/drf_123"),
            ("DELETE", "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts/drf_123"),
        ]

    @pytest.mark.asyncio
    async def test_sends_approved_reply_draft_hash_async(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == (
                "/v1/mailboxes/mbx_123/inbox/threads/thr_123/drafts/drf_123/send"
            )
            assert json.loads(request.content) == {"expected_content_sha256": "b" * 64}
            return json_response(
                {
                    "object": "inbox_reply_draft_send",
                    "draft_id": "drf_123",
                    "status": "sent",
                    "message": {"object": "message", "id": "msg_sent"},
                }
            )

        sent = await make_async_client(handler).mailboxes.send_inbox_reply_draft(
            "mbx_123",
            "thr_123",
            "drf_123",
            expected_content_sha256="b" * 64,
        )

        assert sent["status"] == "sent"

    def test_preserves_legacy_reply_draft_send_without_hash(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.content == b""
            assert request.headers["idempotency-key"] == "legacy-send"
            return json_response(
                {
                    "object": "inbox_reply_draft_send",
                    "draft_id": "drf_123",
                    "status": "sent",
                    "message": {"object": "message", "id": "msg_sent"},
                }
            )

        sent = make_client(handler).mailboxes.send_inbox_reply_draft(
            "mbx_123",
            "thr_123",
            "drf_123",
            {"idempotency_key": "legacy-send"},
        )

        assert sent["status"] == "sent"

    def test_sends_get_mailboxes_id_inbox_threads_thread_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/threads/thr_123"
            return json_response(mock_inbox_thread)

        client = make_client(handler)
        thread = client.mailboxes.get_inbox_thread("mbx_123", "thr_123")
        assert thread["version"] == 7
        assert thread["data"][0]["attachments"][0]["blob_id"] == "blob/123"
        assert thread["data"][0]["authentication_results"]["raw"]["receivedSpf"] == "pass"

    @pytest.mark.asyncio
    async def test_reads_authentication_results_async(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/messages/eml_123"
            return json_response(mock_inbox_messages["data"][0])

        message = await make_async_client(handler).mailboxes.get_inbox_message("mbx_123", "eml_123")
        assert message["authentication_results"]["dmarc"] == "pass"

    def test_creates_new_inbox_draft(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/drafts"
            assert request.headers["idempotency-key"] == "draft-123"
            assert json.loads(request.content) == {
                "to": ["Jane <jane@example.com>"],
                "cc": [{"address": "ops@example.com", "name": None}],
                "subject": "Kickoff",
                "text": "Draft for review.",
            }
            return json_response(mock_inbox_draft, status_code=201)

        client = make_client(handler)
        draft = client.mailboxes.create_inbox_draft(
            "mbx_123",
            {
                "to": ["Jane <jane@example.com>"],
                "cc": [{"address": "ops@example.com", "name": None}],
                "subject": "Kickoff",
                "text": "Draft for review.",
            },
            {"idempotency_key": "draft-123"},
        )
        assert draft["object"] == "inbox_draft"
        assert draft["id"] == "eml_draft"
        assert draft["from"]["address"] == "hello@example.com"
        assert draft["to"][0]["name"] == "Jane"

    @pytest.mark.asyncio
    async def test_creates_new_inbox_draft_async(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/drafts"
            assert json.loads(request.content) == {"to": ["jane@example.com"], "html": "<p>Hi</p>"}
            return json_response(mock_inbox_draft, status_code=201)

        draft = await make_async_client(handler).mailboxes.create_inbox_draft(
            "mbx_123", {"to": ["jane@example.com"], "html": "<p>Hi</p>"}
        )
        assert draft["mailbox_id"] == "mbx_123"
        assert draft["bcc"] == []

    def test_replies_to_inbox_message_with_mailbox_scope(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/messages/eml_123/reply"
            assert json.loads(request.content) == {
                "to": ["jane@example.com"],
                "text": "Thanks for the note.",
            }
            return json_response({"object": "message", "id": "msg_reply"})

        client = make_client(handler)
        message = client.mailboxes.reply_to_inbox_message(
            "mbx_123",
            "eml_123",
            {"to": ["jane@example.com"], "text": "Thanks for the note."},
        )
        assert message["id"] == "msg_reply"

    def test_replies_to_inbox_thread_with_mailbox_scope(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/threads/thr_123/reply"
            return json_response({"object": "message", "id": "msg_thread_reply"})

        client = make_client(handler)
        message = client.mailboxes.reply_to_inbox_thread(
            "mbx_123",
            "thr_123",
            {"to": ["jane@example.com"], "text": "Following up."},
        )
        assert message["id"] == "msg_thread_reply"

    def test_downloads_inbox_attachment_as_bytes(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.headers["accept"] == "application/octet-stream"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/attachments"
            assert str(request.url.params.get("blob_id")) == "blob/123"
            assert str(request.url.params.get("name")) == "invoice.pdf"
            return httpx.Response(200, content=b"\x01\x02\x03")

        client = make_client(handler)
        data = client.mailboxes.download_inbox_attachment(
            "mbx_123",
            {"blob_id": "blob/123", "name": "invoice.pdf"},
        )
        assert data == b"\x01\x02\x03"

    def test_sends_patch_mailboxes_id_inbox_messages_message_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/messages/eml_123"
            body = json.loads(request.content)
            assert body == {"read": True, "starred": False}
            return json_response(mock_inbox_message_action)

        client = make_client(handler)
        result = client.mailboxes.update_inbox_message(
            "mbx_123",
            "eml_123",
            {"read": True, "starred": False},
        )
        assert result["ok"] is True
        assert result["message_id"] == "eml_123"

    def test_sends_post_mailboxes_id_inbox_messages_message_id_move(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/messages/eml_123/move"
            body = json.loads(request.content)
            assert body == {"from_folder_id": "fld_inbox", "target_role": "archive"}
            return json_response(mock_inbox_message_action)

        client = make_client(handler)
        result = client.mailboxes.move_inbox_message(
            "mbx_123",
            "eml_123",
            {"from_folder_id": "fld_inbox", "target_role": "archive"},
        )
        assert result["ok"] is True
        assert result["message_id"] == "eml_123"

    def test_sends_delete_mailboxes_id_inbox_messages_message_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/mailboxes/mbx_123/inbox/messages/eml_123"
            return httpx.Response(204)

        client = make_client(handler)
        result = client.mailboxes.delete_inbox_message("mbx_123", "eml_123")
        assert result is None


class TestMailboxDeliveryRouting:
    def test_gets_and_updates_delivery_routing(self) -> None:
        calls: list[tuple[str, str, object | None]] = []
        response = {
            "object": "mailbox_delivery_routing",
            "mailbox_id": "mbx_source",
            "source_address": "sales@example.com",
            "mode": "fixed",
            "destination_mailbox_id": "mbx_destination",
            "fallback_mailbox_id": "mbx_fallback",
            "activation_state": "pending",
            "activation_error": None,
            "destinations": [],
        }

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content) if request.content else None
            calls.append((request.method, request.url.path, body))
            return json_response(response)

        client = make_client(handler)
        fetched = client.mailboxes.get_delivery_routing("mbx_source")
        updated = client.mailboxes.update_delivery_routing(
            "mbx_source",
            {
                "mode": "fixed",
                "destination_mailbox_id": "mbx_destination",
                "fallback_mailbox_id": "mbx_fallback",
            },
        )

        assert fetched["mode"] == "fixed"
        assert updated["activation_state"] == "pending"
        assert calls == [
            ("GET", "/v1/mailboxes/mbx_source/delivery-routing", None),
            (
                "PATCH",
                "/v1/mailboxes/mbx_source/delivery-routing",
                {
                    "mode": "fixed",
                    "destination_mailbox_id": "mbx_destination",
                    "fallback_mailbox_id": "mbx_fallback",
                },
            ),
        ]


class TestMailboxExports:
    def test_creates_and_reads_mailbox_export(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.raw_path.decode()))
            return json_response(mock_mailbox_export)

        client = make_client(handler)
        created = client.mailboxes.create_export("mbx/123")
        fetched = client.mailboxes.get_export("mbx/123", mock_mailbox_export["id"])

        assert created["status"] == "completed"
        assert fetched["download_url"] == "https://download.test/export.zip"
        assert calls == [
            ("POST", "/v1/mailboxes/mbx%2F123/exports"),
            ("GET", f"/v1/mailboxes/mbx%2F123/exports/{mock_mailbox_export['id']}"),
        ]


class TestImports:
    def test_sends_post_mailboxes_id_imports_imap_source(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports"
            body = json.loads(request.content)
            assert body == {
                "source": {
                    "type": "imap",
                    "provider": "gmail",
                    "email": "old@gmail.com",
                    "password": "app-password",
                },
                "options": {"range": "12m", "include_spam": True},
            }
            return json_response(mock_import, status_code=201)

        client = make_client(handler)
        result = client.mailboxes.create_import(
            "mbx_123",
            {
                "source": {
                    "type": "imap",
                    "provider": "gmail",
                    "email": "old@gmail.com",
                    "password": "app-password",
                },
                "options": {"range": "12m", "include_spam": True},
            },
        )
        assert result["id"] == "imp_abc123"
        assert result["status"] == "running"
        assert result["counts"]["imported"] == 42

    def test_sends_post_mailboxes_id_imports_file_source(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports"
            body = json.loads(request.content)
            assert body == {
                "source": {
                    "type": "files",
                    "provider": "takeout",
                    "file_ids": ["impf_abc123", "impf_def456"],
                }
            }
            return json_response(mock_import, status_code=201)

        client = make_client(handler)
        result = client.mailboxes.create_import(
            "mbx_123",
            {
                "source": {
                    "type": "files",
                    "provider": "takeout",
                    "file_ids": ["impf_abc123", "impf_def456"],
                }
            },
        )
        assert result["id"] == "imp_abc123"

    def test_sends_get_mailboxes_id_imports(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports"
            return json_response(mock_imports)

        client = make_client(handler)
        result = client.mailboxes.list_imports("mbx_123")
        assert result["object"] == "imports"
        assert result["mailbox_id"] == "mbx_123"
        assert result["data"][0]["id"] == "imp_abc123"

    def test_sends_get_mailboxes_id_imports_import_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123"
            return json_response(mock_import_with_folders)

        client = make_client(handler)
        result = client.mailboxes.get_import("mbx_123", "imp_abc123")
        assert result["id"] == "imp_abc123"
        assert result["folders"][0]["source_folder"] == "INBOX"
        assert result["folders"][0]["state"] == "importing"

    def test_sends_post_mailboxes_id_imports_import_id_cancel(self) -> None:
        cancelled = {**mock_import, "status": "cancelled"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123/cancel"
            assert request.content == b""
            return json_response(cancelled)

        client = make_client(handler)
        result = client.mailboxes.cancel_import("mbx_123", "imp_abc123")
        assert result["status"] == "cancelled"

    def test_sends_post_mailboxes_id_imports_import_id_resume(self) -> None:
        resumed = {**mock_import, "status": "queued"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123/resume"
            assert request.content == b""
            return json_response(resumed)

        client = make_client(handler)
        result = client.mailboxes.resume_import("mbx_123", "imp_abc123")
        assert result["status"] == "queued"

    def test_sends_post_mailboxes_id_imports_import_id_restore(self) -> None:
        restored = {**mock_import, "status": "queued"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123/restore"
            body = json.loads(request.content)
            assert body == {"file_ids": ["impf_abc123"]}
            return json_response(restored)

        client = make_client(handler)
        result = client.mailboxes.restore_import(
            "mbx_123",
            "imp_abc123",
            {"file_ids": ["impf_abc123"]},
        )
        assert result["status"] == "queued"

    def test_sends_post_mailboxes_id_imports_import_id_undo(self) -> None:
        undone = {**mock_import, "status": "undo_queued"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123/undo"
            assert request.content == b""
            return json_response(undone)

        client = make_client(handler)
        result = client.mailboxes.undo_import("mbx_123", "imp_abc123")
        assert result["status"] == "undo_queued"

    def test_sends_post_mailboxes_id_imports_files(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/files"
            body = json.loads(request.content)
            assert body == {"provider": "takeout", "file_name": "takeout.mbox", "size_bytes": 1048576}
            return json_response(mock_import_upload, status_code=201)

        client = make_client(handler)
        result = client.mailboxes.create_import_upload(
            "mbx_123",
            {"provider": "takeout", "file_name": "takeout.mbox", "size_bytes": 1048576},
        )
        assert result["object"] == "import_upload"
        assert result["file_id"] == "impf_abc123"
        assert result["parts"][0]["upload_url"].startswith("https://uploads.example.com/")
        assert result["expires_in_seconds"] == 518400

    def test_completes_and_aborts_import_uploads(self) -> None:
        calls: list[tuple[str, str, bytes]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.path, request.content))
            return httpx.Response(status_code=204)

        client = make_client(handler)
        client.mailboxes.complete_import_upload(
            "mbx_123",
            "impf_abc123",
            {"parts": [{"part_number": 1, "etag": '"etag-1"'}]},
        )
        client.mailboxes.abort_import_upload("mbx_123", "impf_abc123")

        assert calls == [
            (
                "POST",
                "/v1/mailboxes/mbx_123/imports/files/impf_abc123/complete",
                b'{"parts":[{"part_number":1,"etag":"\\"etag-1\\""}]}',
            ),
            ("DELETE", "/v1/mailboxes/mbx_123/imports/files/impf_abc123", b""),
        ]


class TestSandboxInboundAsync:
    @pytest.mark.asyncio
    async def test_sends_fake_inbound_to_sandbox_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/sandbox/inbound"
            assert json.loads(request.content)["from"] == "customer@example.com"
            return json_response({"object": "message", "id": "msg_test", "mode": "test"}, status_code=201)

        client = make_async_client(handler)
        message = await client.mailboxes.inject_sandbox_inbound(
            "mbx_123",
            {"from_": "customer@example.com", "subject": "Sandbox reply", "text": "Looks good"},
        )

        assert message["mode"] == "test"


class TestSuspensionAsync:
    @pytest.mark.asyncio
    async def test_suspends_and_resumes_mailbox(self) -> None:
        paths: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            paths.append(request.url.path)
            return json_response(mock_mailbox)

        client = make_async_client(handler)
        await client.mailboxes.suspend("mbx_123")
        await client.mailboxes.resume("mbx_123")

        assert paths == ["/v1/mailboxes/mbx_123/suspend", "/v1/mailboxes/mbx_123/resume"]


class TestForwardingAsync:
    @pytest.mark.asyncio
    async def test_lists_creates_and_deletes_forwarding(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.path))
            if request.method == "GET":
                return json_response(mock_forwarding_list)
            if request.method == "POST":
                return json_response(mock_forwarding)
            return httpx.Response(204)

        client = make_async_client(handler)
        await client.mailboxes.list_forwarding("mbx_123")
        await client.mailboxes.create_forwarding("mbx_123", {"destination": "owner@example.net"})
        await client.mailboxes.delete_forwarding("mbx_123", "fwd_0123456789abcdefghjkmnpq")

        assert calls == [
            ("GET", "/v1/mailboxes/mbx_123/forwarding"),
            ("POST", "/v1/mailboxes/mbx_123/forwarding"),
            (
                "DELETE",
                "/v1/mailboxes/mbx_123/forwarding/fwd_0123456789abcdefghjkmnpq",
            ),
        ]


class TestMailboxDeliveryRoutingAsync:
    @pytest.mark.asyncio
    async def test_gets_and_updates_delivery_routing(self) -> None:
        calls: list[str] = []
        response = {
            "object": "mailbox_delivery_routing",
            "mailbox_id": "mbx_source",
            "source_address": "sales@example.com",
            "mode": "keep",
            "destinations": [],
        }

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(f"{request.method} {request.url.path}")
            return json_response(response)

        client = make_async_client(handler)
        await client.mailboxes.get_delivery_routing("mbx_source")
        await client.mailboxes.update_delivery_routing("mbx_source", {"mode": "keep"})

        assert calls == [
            "GET /v1/mailboxes/mbx_source/delivery-routing",
            "PATCH /v1/mailboxes/mbx_source/delivery-routing",
        ]


class TestMailboxExportsAsync:
    @pytest.mark.asyncio
    async def test_creates_and_reads_mailbox_export(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.path))
            return json_response(mock_mailbox_export)

        client = make_async_client(handler)
        created = await client.mailboxes.create_export("mbx_123")
        fetched = await client.mailboxes.get_export("mbx_123", mock_mailbox_export["id"])

        assert created["id"] == mock_mailbox_export["id"]
        assert fetched["status"] == "completed"
        assert calls == [
            ("POST", "/v1/mailboxes/mbx_123/exports"),
            ("GET", f"/v1/mailboxes/mbx_123/exports/{mock_mailbox_export['id']}"),
        ]


class TestImportsAsync:
    @pytest.mark.asyncio
    async def test_sends_post_mailboxes_id_imports(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports"
            body = json.loads(request.content)
            assert body == {
                "source": {
                    "type": "imap",
                    "provider": "fastmail",
                    "email": "old@fastmail.com",
                    "password": "app-password",
                }
            }
            return json_response(mock_import, status_code=201)

        client = make_async_client(handler)
        result = await client.mailboxes.create_import(
            "mbx_123",
            {
                "source": {
                    "type": "imap",
                    "provider": "fastmail",
                    "email": "old@fastmail.com",
                    "password": "app-password",
                }
            },
        )
        assert result["id"] == "imp_abc123"

    @pytest.mark.asyncio
    async def test_sends_get_mailboxes_id_imports(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports"
            return json_response(mock_imports)

        client = make_async_client(handler)
        result = await client.mailboxes.list_imports("mbx_123")
        assert result["data"][0]["id"] == "imp_abc123"

    @pytest.mark.asyncio
    async def test_sends_get_mailboxes_id_imports_import_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123"
            return json_response(mock_import_with_folders)

        client = make_async_client(handler)
        result = await client.mailboxes.get_import("mbx_123", "imp_abc123")
        assert result["folders"][0]["target_folder"] == "Inbox"

    @pytest.mark.asyncio
    async def test_sends_post_mailboxes_id_imports_import_id_cancel(self) -> None:
        cancelled = {**mock_import, "status": "cancelled"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123/cancel"
            assert request.content == b""
            return json_response(cancelled)

        client = make_async_client(handler)
        result = await client.mailboxes.cancel_import("mbx_123", "imp_abc123")
        assert result["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_sends_post_mailboxes_id_imports_import_id_resume(self) -> None:
        resumed = {**mock_import, "status": "queued"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123/resume"
            assert request.content == b""
            return json_response(resumed)

        client = make_async_client(handler)
        result = await client.mailboxes.resume_import("mbx_123", "imp_abc123")
        assert result["status"] == "queued"

    @pytest.mark.asyncio
    async def test_sends_post_mailboxes_id_imports_import_id_restore(self) -> None:
        restored = {**mock_import, "status": "queued"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123/restore"
            body = json.loads(request.content)
            assert body == {"file_ids": ["impf_abc123"]}
            return json_response(restored)

        client = make_async_client(handler)
        result = await client.mailboxes.restore_import(
            "mbx_123",
            "imp_abc123",
            {"file_ids": ["impf_abc123"]},
        )
        assert result["status"] == "queued"

    @pytest.mark.asyncio
    async def test_sends_post_mailboxes_id_imports_import_id_undo(self) -> None:
        undone = {**mock_import, "status": "undo_queued"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/imp_abc123/undo"
            assert request.content == b""
            return json_response(undone)

        client = make_async_client(handler)
        result = await client.mailboxes.undo_import("mbx_123", "imp_abc123")
        assert result["status"] == "undo_queued"

    @pytest.mark.asyncio
    async def test_sends_post_mailboxes_id_imports_files(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/mailboxes/mbx_123/imports/files"
            body = json.loads(request.content)
            assert body == {"provider": "file", "file_name": "export.zip", "size_bytes": 2048}
            return json_response(mock_import_upload, status_code=201)

        client = make_async_client(handler)
        result = await client.mailboxes.create_import_upload(
            "mbx_123",
            {"provider": "file", "file_name": "export.zip", "size_bytes": 2048},
        )
        assert result["file_id"] == "impf_abc123"

    @pytest.mark.asyncio
    async def test_completes_and_aborts_import_uploads(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.path))
            return httpx.Response(status_code=204)

        client = make_async_client(handler)
        await client.mailboxes.complete_import_upload(
            "mbx_123",
            "impf_abc123",
            {"parts": [{"part_number": 1, "etag": '"etag-1"'}]},
        )
        await client.mailboxes.abort_import_upload("mbx_123", "impf_abc123")

        assert calls == [
            ("POST", "/v1/mailboxes/mbx_123/imports/files/impf_abc123/complete"),
            ("DELETE", "/v1/mailboxes/mbx_123/imports/files/impf_abc123"),
        ]


class TestAppPasswords:
    def test_creates_lists_and_revokes(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.raw_path.decode()))
            if request.method == "POST":
                assert json.loads(request.content) == {
                    "name": "Embedded webmail",
                    "allowed_cidrs": ["203.0.113.0/24"],
                }
                return json_response(
                    {
                        "object": "mailbox_app_password",
                        "id": "appwd_123",
                        "mailbox_id": "mbx_123",
                        "name": "Embedded webmail",
                        "state": "active",
                        "purpose": "operator_client",
                        "expires_at": "2026-10-15T00:00:00.000Z",
                        "allowed_cidrs": ["203.0.113.0/24"],
                        "last_used_at": None,
                        "created_at": "2026-07-15T00:00:00.000Z",
                        "revoked_at": None,
                        "secret": "app_once",
                    },
                    status_code=201,
                )
            if request.method == "DELETE":
                return httpx.Response(204)
            return json_response({"object": "list", "data": []})

        client = make_client(handler)
        created = client.mailboxes.create_app_password(
            "mbx_123",
            {"name": "Embedded webmail", "allowed_cidrs": ["203.0.113.0/24"]},
        )
        client.mailboxes.list_app_passwords("mbx_123")
        client.mailboxes.revoke_app_password("mbx_123", "appwd:opaque/123")

        assert created["secret"] == "app_once"
        assert calls == [
            ("POST", "/v1/mailboxes/mbx_123/app-passwords"),
            ("GET", "/v1/mailboxes/mbx_123/app-passwords"),
            ("DELETE", "/v1/mailboxes/mbx_123/app-passwords/appwd%3Aopaque%2F123"),
        ]
