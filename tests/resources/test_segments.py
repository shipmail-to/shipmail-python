from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

definition = {
    "match": "all",
    "rules": [{"kind": "merge_field", "field": "role", "operator": "equals", "value": "founder"}],
}

mock_segment = {
    "object": "segment",
    "id": "nwsseg_1",
    "audience_id": "aud_123",
    "name": "Founders",
    "definition": definition,
    "matching_count": 4,
    "created_at": "2026-11-03T00:00:00Z",
    "updated_at": "2026-11-03T00:00:00Z",
}


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/v1/audiences/aud_123/segments":
        if request.method == "POST":
            assert json.loads(request.content) == {"name": "Founders", "definition": definition}
            return json_response(mock_segment, 201)
        assert request.method == "GET"
        return json_response({"data": [mock_segment]})
    assert path == "/v1/audiences/aud_123/segments/nwsseg_1"
    if request.method == "DELETE":
        return httpx.Response(204)
    if request.method == "PATCH":
        assert json.loads(request.content) == {"name": "All founders"}
    else:
        assert request.method == "GET"
    return json_response(mock_segment)


class TestSegments:
    def test_sync_calls(self) -> None:
        client = make_client(_handler)
        assert client.audiences.segments.list("aud_123")["data"][0]["matching_count"] == 4
        created = client.audiences.segments.create("aud_123", {"name": "Founders", "definition": definition})
        assert created["id"] == "nwsseg_1"
        assert client.audiences.segments.get("aud_123", "nwsseg_1")["name"] == "Founders"
        client.audiences.segments.update("aud_123", "nwsseg_1", {"name": "All founders"})
        assert client.audiences.segments.delete("aud_123", "nwsseg_1") is None

    @pytest.mark.asyncio
    async def test_async_calls(self) -> None:
        client = make_async_client(_handler)
        listed = await client.audiences.segments.list("aud_123")
        assert listed["data"][0]["object"] == "segment"
        await client.audiences.segments.create("aud_123", {"name": "Founders", "definition": definition})
        await client.audiences.segments.get("aud_123", "nwsseg_1")
        await client.audiences.segments.update("aud_123", "nwsseg_1", {"name": "All founders"})
        assert await client.audiences.segments.delete("aud_123", "nwsseg_1") is None
