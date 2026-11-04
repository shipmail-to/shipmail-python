from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_queue = {
    "object": "event_queue",
    "id": "evq_123",
    "events": ["message.received", "message.bounced"],
    "description": "Inbound for my agent",
    "mailbox_ids": None,
    "domain_ids": None,
    "include_reply_text": False,
    "authenticated_senders_only": False,
    "allowed_senders": None,
    "created_at": "2026-11-04T10:00:00.000Z",
}

mock_events = {
    "data": [
        {
            "version": "2026-07-20",
            "event_id": "evt_001",
            "event_type": "message.received",
            "created_at": "2026-11-04T10:01:00.000Z",
            "test": False,
            "data": {"message_id": "msg_1"},
        }
    ],
    "has_more": True,
}


class TestCreate:
    def test_sends_post_event_queues_with_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/event-queues"
            assert json.loads(request.content) == {
                "events": ["message.received", "message.bounced"],
                "description": "Inbound for my agent",
                "allowed_senders": ["customer.com"],
            }
            return json_response({**mock_queue, "allowed_senders": ["customer.com"]}, 201)

        queue = make_client(handler).event_queues.create(
            {
                "events": ["message.received", "message.bounced"],
                "description": "Inbound for my agent",
                "allowed_senders": ["customer.com"],
            }
        )
        assert queue["id"] == "evq_123"
        assert queue["allowed_senders"] == ["customer.com"]


class TestList:
    def test_sends_get_event_queues(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/event-queues"
            return json_response({"data": [mock_queue], "pagination": {"next_cursor": None, "has_more": False}})

        result = make_client(handler).event_queues.list()
        assert result["data"][0]["id"] == "evq_123"

    def test_sends_cursor_and_limit(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["cursor"] == "cur_abc"
            assert request.url.params["limit"] == "50"
            return json_response({"data": [], "pagination": {"next_cursor": None, "has_more": False}})

        make_client(handler).event_queues.list({"cursor": "cur_abc", "limit": 50})


class TestGet:
    def test_sends_get_event_queues_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/event-queues/evq_123"
            return json_response(mock_queue)

        queue = make_client(handler).event_queues.get("evq_123")
        assert queue["events"] == ["message.received", "message.bounced"]

    def test_encodes_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.raw_path == b"/v1/event-queues/a%2Fb"
            return json_response(mock_queue)

        make_client(handler).event_queues.get("a/b")


class TestDelete:
    def test_sends_delete_event_queues_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/event-queues/evq_123"
            return httpx.Response(204)

        assert make_client(handler).event_queues.delete("evq_123") is None


class TestListEvents:
    def test_sends_get_events_with_limit(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/event-queues/evq_123/events"
            assert request.url.params["limit"] == "100"
            return json_response(mock_events)

        result = make_client(handler).event_queues.list_events("evq_123", {"limit": 100})
        assert result["has_more"] is True
        assert result["data"][0]["event_id"] == "evt_001"

    def test_omits_limit_when_absent(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "limit" not in request.url.params
            return json_response({"data": [], "has_more": False})

        result = make_client(handler).event_queues.list_events("evq_123")
        assert result["data"] == []


class TestAck:
    def test_sends_post_ack_with_event_ids(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/event-queues/evq_123/events/ack"
            assert json.loads(request.content) == {"event_ids": ["evt_001", "evt_002"]}
            return json_response({"acknowledged": 1})

        result = make_client(handler).event_queues.ack("evq_123", ["evt_001", "evt_002"])
        assert result["acknowledged"] == 1


class TestAsync:
    @pytest.mark.asyncio
    async def test_reads_and_acks(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.method == "GET":
                assert request.url.path == "/v1/event-queues/evq_123/events"
                return json_response(mock_events)
            assert request.url.path == "/v1/event-queues/evq_123/events/ack"
            assert json.loads(request.content) == {"event_ids": ["evt_001"]}
            return json_response({"acknowledged": 1})

        client = make_async_client(handler)
        events = await client.event_queues.list_events("evq_123", {"limit": 10})
        result = await client.event_queues.ack("evq_123", [e["event_id"] for e in events["data"]])
        assert result["acknowledged"] == 1

    @pytest.mark.asyncio
    async def test_creates_gets_and_deletes(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path.startswith("/v1/event-queues")
            if request.method == "DELETE":
                return httpx.Response(204)
            return json_response(mock_queue, 201 if request.method == "POST" else 200)

        client = make_async_client(handler)
        created = await client.event_queues.create({"events": ["message.received"]})
        fetched = await client.event_queues.get(created["id"])
        assert fetched["id"] == "evq_123"
        assert await client.event_queues.delete("evq_123") is None
