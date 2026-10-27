from __future__ import annotations

import json

import httpx
import pytest

from shipmail import Message
from tests.conftest import json_response, make_async_client, make_client

mock_message: Message = {
    "object": "message",
    "id": "msg_123",
    "mailbox_id": "mbx_456",
    "thread_id": "thr_789",
    "conversation_id": "thd_789",
    "source_rfc_message_id": "<crm-123@example.com>",
    "delivered_rfc_message_id": None,
    "client_reference": "crm-123",
    "metadata": {"campaign": "onboarding"},
    "headers": [{"name": "List-Unsubscribe-Post", "value": "List-Unsubscribe=One-Click"}],
    "subject": "Hello",
    "from_address": "hello@example.com",
    "to_addresses": [{"address": "user@example.com", "name": "User"}],
    "cc_addresses": None,
    "bcc_addresses": None,
    "attachments": None,
    "source": "api",
    "mode": "live",
    "status": "queued",
    "rule_disposition": None,
    "scheduled_at": None,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

mock_inbound_message: Message = {
    **mock_message,
    "source": "inbound",
    "status": "delivered",
    "rule_disposition": {
        "matched_rule_ids": ["rule_invoices", "rule_priority"],
        "stop_rule_id": "rule_priority",
    },
}


class TestSend:
    def test_sends_post_messages_with_html(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/messages"
            body = json.loads(request.content)
            assert body == {
                "from": "hello@example.com",
                "to": ["user@example.com"],
                "subject": "Hello",
                "html": "<p>Hi there</p>",
            }
            return json_response(mock_message)

        client = make_client(handler)
        message = client.messages.send(
            {
                "from": "hello@example.com",
                "to": ["user@example.com"],
                "subject": "Hello",
                "html": "<p>Hi there</p>",
            }
        )
        assert message["id"] == "msg_123"
        assert message["status"] == "queued"

    def test_sends_with_mailbox_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["mailbox_id"] == "mbx_456"
            return json_response(mock_message)

        client = make_client(handler)
        client.messages.send(
            {
                "mailbox_id": "mbx_456",
                "to": [{"address": "user@example.com"}],
                "subject": "Test",
                "html": "<p>Hi</p>",
            }
        )

    def test_sends_with_cc_bcc_and_reply_to(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["cc"] == [{"address": "cc@example.com"}]
            assert body["bcc"] == [{"address": "bcc@example.com"}]
            assert body["reply_to"] == {"address": "reply@example.com", "name": "Reply"}
            return json_response(mock_message)

        client = make_client(handler)
        client.messages.send(
            {
                "mailbox_id": "mbx_456",
                "to": [{"address": "user@example.com"}],
                "subject": "Test",
                "text": "test",
                "cc": [{"address": "cc@example.com"}],
                "bcc": [{"address": "bcc@example.com"}],
                "reply_to": {"address": "reply@example.com", "name": "Reply"},
            }
        )

    def test_sends_with_text_only(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["text"] == "Plain text"
            assert "html" not in body
            return json_response(mock_message)

        client = make_client(handler)
        client.messages.send(
            {
                "mailbox_id": "mbx_456",
                "to": [{"address": "user@example.com"}],
                "subject": "Test",
                "text": "Plain text",
            }
        )

    def test_sends_with_string_recipients(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["to"] == ["user@example.com"]
            return json_response(mock_message)

        client = make_client(handler)
        client.messages.send(
            {
                "from": "hello@example.com",
                "to": ["user@example.com"],
                "subject": "Test",
                "text": "Hi",
            }
        )

    def test_sends_with_in_reply_to_and_references(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["in_reply_to"] == "<msg-id-1@example.com>"
            assert body["references"] == ["<msg-id-0@example.com>", "<msg-id-1@example.com>"]
            assert body["track_reply"] is True
            return json_response(mock_message)

        client = make_client(handler)
        client.messages.send(
            {
                "mailbox_id": "mbx_456",
                "to": [{"address": "user@example.com"}],
                "subject": "Re: Test",
                "html": "<p>Reply</p>",
                "in_reply_to": "<msg-id-1@example.com>",
                "references": ["<msg-id-0@example.com>", "<msg-id-1@example.com>"],
                "track_reply": True,
            }
        )

    def test_sends_durable_correlation_metadata_and_headers(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["client_reference"] == "crm-123"
            assert body["metadata"] == {"campaign": "onboarding", "sequence": 2}
            assert body["source_rfc_message_id"] == "<crm-123@example.com>"
            assert body["headers"] == [
                {
                    "name": "List-Unsubscribe",
                    "value": "<https://example.com/unsubscribe/123>",
                }
            ]
            return json_response(mock_message)

        client = make_client(handler)
        client.messages.send(
            {
                "mailbox_id": "mbx_456",
                "to": ["user@example.com"],
                "subject": "Hello",
                "text": "Hi",
                "client_reference": "crm-123",
                "metadata": {"campaign": "onboarding", "sequence": 2},
                "source_rfc_message_id": "<crm-123@example.com>",
                "headers": [
                    {
                        "name": "List-Unsubscribe",
                        "value": "<https://example.com/unsubscribe/123>",
                    }
                ],
            }
        )

    def test_sends_a_stored_template_without_subject_or_body(self) -> None:
        template_body = {"id": "tpl_123", "version": 2, "variables": {"first_name": "Ada", "seats": 3}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/messages"
            assert json.loads(request.content) == {
                "mailbox_id": "mbx_456",
                "to": ["user@example.com"],
                "template": template_body,
            }
            return json_response(mock_message, 201)

        client = make_client(handler)
        result = client.messages.send(
            {
                "mailbox_id": "mbx_456",
                "to": ["user@example.com"],
                "template": {"id": "tpl_123", "version": 2, "variables": {"first_name": "Ada", "seats": 3}},
            }
        )
        assert result["id"] == "msg_123"

    @pytest.mark.asyncio
    async def test_async_sends_a_stored_template(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {
                "mailbox_id": "mbx_456",
                "to": ["user@example.com"],
                "template": {"id": "tpl_123"},
            }
            return json_response(mock_message, 201)

        client = make_async_client(handler)
        result = await client.messages.send(
            {"mailbox_id": "mbx_456", "to": ["user@example.com"], "template": {"id": "tpl_123"}}
        )
        assert result["id"] == "msg_123"


class TestList:
    def test_sends_get_messages_with_mailbox_id(self) -> None:
        response = {
            "data": [mock_inbound_message],
            "pagination": {"next_cursor": None, "has_more": False, "limit": 25},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/messages"
            assert str(request.url.params.get("mailbox_id")) == "mbx_456"
            return json_response(response)

        client = make_client(handler)
        result = client.messages.list({"mailbox_id": "mbx_456"})
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == "msg_123"
        rule_disposition = result["data"][0]["rule_disposition"]
        assert rule_disposition is not None
        assert rule_disposition["matched_rule_ids"] == [
            "rule_invoices",
            "rule_priority",
        ]
        assert result["pagination"]["limit"] == 25

    def test_looks_up_by_client_reference_without_mailbox_id(self) -> None:
        response = {
            "data": [mock_message],
            "pagination": {"next_cursor": None, "has_more": False, "limit": 25},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params.get("mailbox_id") is None
            assert request.url.params.get("client_reference") == "crm-123"
            return json_response(response)

        client = make_client(handler)
        result = client.messages.list({"client_reference": "crm-123"})
        assert result["data"][0]["client_reference"] == "crm-123"


class TestListAnalytics:
    def test_sends_bounded_incremental_analytics_query(self) -> None:
        response = {
            "data": [],
            "pagination": {
                "next_cursor": None,
                "has_more": False,
                "limit": 100,
                "snapshot_at": "2026-07-29T00:00:00.000Z",
            },
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/messages/analytics"
            assert request.url.params.get("updated_after") == "2026-07-01T00:00:00.000Z"
            assert request.url.params.get("updated_before") == "2026-07-29T00:00:00.000Z"
            assert request.url.params.get("cursor") == "cursor_123"
            assert request.url.params.get("limit") == "100"
            return json_response(response)

        client = make_client(handler)
        result = client.messages.list_analytics(
            {
                "updated_after": "2026-07-01T00:00:00.000Z",
                "updated_before": "2026-07-29T00:00:00.000Z",
                "cursor": "cursor_123",
                "limit": 100,
            }
        )
        assert result["pagination"]["snapshot_at"] == "2026-07-29T00:00:00.000Z"


class TestGet:
    def test_sends_get_messages_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/messages/msg_123"
            return json_response(mock_inbound_message)

        client = make_client(handler)
        message = client.messages.get("msg_123")
        assert message["id"] == "msg_123"
        assert message["mailbox_id"] == "mbx_456"
        assert message["thread_id"] == "thr_789"
        assert message["conversation_id"] == "thd_789"
        assert message["source"] == "inbound"
        assert message["rule_disposition"] is not None
        assert message["rule_disposition"]["stop_rule_id"] == "rule_priority"


class TestReply:
    def test_sends_post_messages_id_reply(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/messages/msg_123/reply"
            body = json.loads(request.content)
            assert body["to"] == ["user@example.com"]
            assert body["text"] == "Reply text"
            return json_response(mock_message)

        client = make_client(handler)
        message = client.messages.reply(
            "msg_123",
            {
                "to": ["user@example.com"],
                "text": "Reply text",
            },
        )
        assert message["id"] == "msg_123"
