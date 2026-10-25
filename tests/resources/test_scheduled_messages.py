from __future__ import annotations

import json
from urllib.parse import parse_qs

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

SCHEDULED_MESSAGE = {
    "object": "scheduled_message",
    "id": "msg_123",
    "scheduled_message_id": "sch_123",
    "status": "settling",
    "kind": "scheduled",
    "mailbox_id": "mbx_123",
    "mailbox_address": "hello@example.com",
    "from_address": "hello@example.com",
    "identity_id": "ident_123",
    "mode": "live",
    "subject": "Hello",
    "to": [{"address": "customer@example.net", "name": None}],
    "cc": [],
    "bcc": [],
    "attachments": [],
    "scheduled_at": "2026-08-01T08:00:00.000Z",
    "created_at": "2026-07-24T12:00:00.000Z",
    "updated_at": "2026-07-24T12:00:00.000Z",
    "last_error": None,
}


class TestScheduledMessages:
    def test_list_serializes_filters(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/scheduled-messages"
            query = parse_qs(request.url.query.decode())
            assert query == {
                "include_held": ["true"],
                "search": ["Christelle"],
                "limit": ["25"],
            }
            return json_response(
                {
                    "object": "scheduled_message_list",
                    "data": [SCHEDULED_MESSAGE],
                    "total": 1,
                }
            )

        result = make_client(handler).scheduled_messages.list(
            {"include_held": True, "search": "Christelle", "limit": 25}
        )
        assert result["data"][0]["id"] == "msg_123"
        assert result["data"][0].get("status") == "settling"

    def test_get_update_and_cancel(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.method == "DELETE":
                return httpx.Response(204)
            return json_response(SCHEDULED_MESSAGE)

        client = make_client(handler)
        client.scheduled_messages.get("msg_123")
        client.scheduled_messages.update(
            "msg_123",
            {
                "to": ["customer@example.net"],
                "subject": "Updated",
                "text": "Updated body",
                "staged_attachment_ids": ["sat_123"],
                "scheduled_at": "2026-08-02T08:00:00.000Z",
            },
            {"idempotency_key": "update-123"},
        )
        client.scheduled_messages.cancel("msg_123")

        assert [request.method for request in requests] == ["GET", "PATCH", "DELETE"]
        assert all(request.url.path == "/v1/scheduled-messages/msg_123" for request in requests)
        assert json.loads(requests[1].content)["staged_attachment_ids"] == ["sat_123"]
        assert requests[1].headers["idempotency-key"] == "update-123"


class TestAsyncScheduledMessages:
    @pytest.mark.asyncio
    async def test_lists_and_cancels(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.method == "DELETE":
                return httpx.Response(204)
            return json_response(
                {
                    "object": "scheduled_message_list",
                    "data": [SCHEDULED_MESSAGE],
                    "total": 1,
                }
            )

        client = make_async_client(handler)
        result = await client.scheduled_messages.list()
        await client.scheduled_messages.cancel("msg_123")

        assert result["total"] == 1
        assert [request.method for request in requests] == ["GET", "DELETE"]
