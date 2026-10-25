from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_scan = {
    "object": "reply_scan",
    "id": "rsc_123",
    "mailbox_ids": ["mbx_123"],
    "after": "2025-07-20T00:00:00.000Z",
    "before": "2026-07-20T00:00:00.000Z",
    "snapshot_at": "2026-07-20T00:00:00.000Z",
    "status": "completed",
    "candidate_count": 1,
    "completed_at": "2026-07-20T00:00:02.000Z",
    "created_at": "2026-07-20T00:00:00.000Z",
}


class TestReplyScans:
    def test_create_get_and_list_results(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.raw_path.decode()))
            if request.method == "POST":
                assert json.loads(request.content) == {
                    "mailbox_ids": ["mbx_123"],
                    "after": "2025-07-20T00:00:00.000Z",
                    "before": "2026-07-20T00:00:00.000Z",
                }
                return json_response(mock_scan, 201)
            if request.url.path.endswith("/results"):
                return json_response(
                    {
                        "object": "reply_scan_results",
                        "scan_id": "rsc/123",
                        "data": [],
                        "pagination": {"limit": 25, "has_more": False, "next_cursor": None},
                    }
                )
            return json_response(mock_scan)

        client = make_client(handler)
        created = client.reply_scans.create(
            {
                "mailbox_ids": ["mbx_123"],
                "after": "2025-07-20T00:00:00.000Z",
                "before": "2026-07-20T00:00:00.000Z",
            }
        )
        fetched = client.reply_scans.get("rsc/123")
        results = client.reply_scans.list_results("rsc/123", {"cursor": "opaque cursor", "limit": 25})

        assert created["id"] == "rsc_123"
        assert fetched["status"] == "completed"
        assert results["scan_id"] == "rsc/123"
        assert calls == [
            ("POST", "/v1/reply-scans"),
            ("GET", "/v1/reply-scans/rsc%2F123"),
            ("GET", "/v1/reply-scans/rsc%2F123/results?cursor=opaque+cursor&limit=25"),
        ]

    @pytest.mark.asyncio
    async def test_async_create_is_available(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/reply-scans"
            return json_response(mock_scan, 201)

        client = make_async_client(handler)
        result = await client.reply_scans.create(
            {
                "mailbox_ids": ["mbx_123"],
                "after": "2025-07-20T00:00:00.000Z",
            }
        )
        assert result["id"] == "rsc_123"
        await client.aclose()
