from __future__ import annotations

import json

import httpx

from tests.conftest import json_response, make_client

mock_message = {
    "object": "message",
    "id": "msg_123",
    "mailbox_id": "mbx_456",
    "thread_id": "thr_789",
    "conversation_id": "thd_789",
    "subject": "Test thread",
    "from_address": "hello@example.com",
    "to_addresses": [{"address": "user@example.com"}],
    "cc_addresses": None,
    "bcc_addresses": None,
    "source": "api",
    "status": "sent",
    "rule_disposition": None,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

mock_message_2 = {
    "object": "message",
    "id": "msg_124",
    "mailbox_id": "mbx_456",
    "thread_id": "thr_789",
    "conversation_id": "thd_789",
    "subject": "Re: Test thread",
    "from_address": "user@example.com",
    "to_addresses": [{"address": "hello@example.com"}],
    "cc_addresses": None,
    "bcc_addresses": None,
    "source": "inbound",
    "status": "delivered",
    "rule_disposition": {
        "matched_rule_ids": ["rule_support"],
        "stop_rule_id": None,
    },
    "created_at": "2025-01-02T00:00:00Z",
    "updated_at": "2025-01-02T00:00:00Z",
}

mock_thread = {
    "object": "thread",
    "id": "thr_789",
    "mailbox_id": "mbx_456",
    "subject": "Re: Test thread",
    "message_count": 2,
    "latest_message": mock_message_2,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-02T00:00:00Z",
}


class TestList:
    def test_sends_get_threads_with_mailbox_id(self) -> None:
        response = {
            "data": [mock_thread],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/threads"
            assert str(request.url.params.get("mailbox_id")) == "mbx_456"
            return json_response(response)

        client = make_client(handler)
        result = client.threads.list({"mailbox_id": "mbx_456"})
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == "thr_789"
        assert result["data"][0]["latest_message"]["id"] == "msg_124"
        assert result["data"][0]["latest_message"]["rule_disposition"]["matched_rule_ids"] == [
            "rule_support"
        ]

    def test_sends_cursor_and_limit_query_params(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url.params.get("mailbox_id")) == "mbx_456"
            assert str(request.url.params.get("cursor")) == "cur_abc"
            assert str(request.url.params.get("limit")) == "20"
            return json_response(response)

        client = make_client(handler)
        client.threads.list({
            "mailbox_id": "mbx_456",
            "cursor": "cur_abc",
            "limit": 20,
        })


class TestGet:
    def test_sends_get_threads_id(self) -> None:
        response = {
            "data": [mock_message, mock_message_2],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/threads/thr_789"
            assert request.url.params.get("mailbox_id") == "mbx_456"
            return json_response(response)

        client = make_client(handler)
        result = client.threads.get("thr_789", {"mailbox_id": "mbx_456"})
        assert len(result["data"]) == 2
        assert result["data"][0]["id"] == "msg_123"
        assert result["data"][1]["id"] == "msg_124"

    def test_sends_cursor_and_limit_params(self) -> None:
        response = {
            "data": [mock_message_2],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url.params.get("cursor")) == "cur_xyz"
            assert str(request.url.params.get("limit")) == "5"
            return json_response(response)

        client = make_client(handler)
        client.threads.get(
            "thr_789", {"mailbox_id": "mbx_456", "cursor": "cur_xyz", "limit": 5}
        )

    def test_omits_undefined_params(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert "cursor" not in request.url.params
            assert "limit" not in request.url.params
            return json_response(response)

        client = make_client(handler)
        client.threads.get("thr_789", {"mailbox_id": "mbx_456"})


class TestReply:
    def test_sends_sandbox_outcome(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["sandbox_outcome"] == "complained"
            return json_response({**mock_message, "mode": "test", "status": "complained"})

        client = make_client(handler)
        message = client.threads.reply("thr_789", {
            "mailbox_id": "mbx_456",
            "to": ["user@example.com"],
            "text": "Sandbox reply",
            "sandbox_outcome": "complained",
        })
        assert message["mode"] == "test"

    def test_sends_post_threads_id_reply_with_body(self) -> None:
        reply_message = {
            "object": "message",
            "id": "msg_125",
            "mailbox_id": "mbx_456",
            "thread_id": "thr_789",
            "conversation_id": "thd_789",
            "subject": "Re: Test thread",
            "from_address": "hello@example.com",
            "to_addresses": [{"address": "user@example.com"}],
            "cc_addresses": None,
            "bcc_addresses": None,
            "source": "api",
            "status": "queued",
            "created_at": "2025-01-03T00:00:00Z",
            "updated_at": "2025-01-03T00:00:00Z",
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/threads/thr_789/reply"
            body = json.loads(request.content)
            assert body == {
                "mailbox_id": "mbx_456",
                "to": ["user@example.com"],
                "html": "<p>Thanks for your message</p>",
            }
            return json_response(reply_message)

        client = make_client(handler)
        message = client.threads.reply("thr_789", {
            "mailbox_id": "mbx_456",
            "to": ["user@example.com"],
            "html": "<p>Thanks for your message</p>",
        })
        assert message["id"] == "msg_125"
        assert message["thread_id"] == "thr_789"
        assert message["conversation_id"] == "thd_789"

    def test_sends_reply_with_to_and_cc_overrides(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["to"] == [{"address": "other@example.com"}]
            assert body["cc"] == [{"address": "cc@example.com", "name": "CC User"}]
            assert body["text"] == "Plain reply"
            return json_response(mock_message)

        client = make_client(handler)
        client.threads.reply("thr_789", {
            "mailbox_id": "mbx_456",
            "text": "Plain reply",
            "to": [{"address": "other@example.com"}],
            "cc": [{"address": "cc@example.com", "name": "CC User"}],
        })

    def test_sends_scheduled_reply(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["text"] == "Later"
            assert body["scheduled_at"] == "2026-06-07T09:30:00.000Z"
            return json_response(mock_message)

        client = make_client(handler)
        client.threads.reply("thr_789", {
            "mailbox_id": "mbx_456",
            "to": ["user@example.com"],
            "text": "Later",
            "scheduled_at": "2026-06-07T09:30:00.000Z",
        })
