from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_step = {
    "object": "welcome_step",
    "id": "nwswstp_1",
    "audience_id": "aud_123",
    "position": 1,
    "wait_minutes": 60,
    "sender_identity_id": "nwsid_1",
    "subject": "Welcome",
    "preview_text": None,
    "blocks": [{"type": "paragraph", "body": "Hi"}],
    "track_engagement": False,
    "add_utm_tags": False,
    "styling_mode": "styled",
    "sent_count": 0,
    "delivered_count": 0,
    "bounced_count": 0,
    "complained_count": 0,
    "created_at": "2026-10-15T00:00:00Z",
    "updated_at": "2026-10-15T00:00:00Z",
}

mock_sequence = {
    "object": "welcome_sequence",
    "audience_id": "aud_123",
    "enabled": True,
    "paused": False,
    "pause_reason": None,
    "active_readers": 3,
    "completed_readers": 1,
    "steps": [mock_step],
}


def _handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/v1/audiences/aud_123/welcome-sequence":
        if request.method == "PATCH":
            assert json.loads(request.content) == {"enabled": True}
        return json_response(mock_sequence)
    if path == "/v1/audiences/aud_123/welcome-sequence/steps":
        assert request.method == "POST"
        assert json.loads(request.content) == {"subject": "Welcome", "content_markdown": "# Hi"}
        return json_response(mock_step, 201)
    assert path == "/v1/audiences/aud_123/welcome-sequence/steps/nwswstp_1"
    if request.method == "DELETE":
        return json_response({"object": "welcome_step", "id": "nwswstp_1", "deleted": True})
    assert request.method == "PATCH"
    assert json.loads(request.content) == {"wait_minutes": 0}
    return json_response(mock_step)


class TestWelcomeSequence:
    def test_sync_calls(self) -> None:
        client = make_client(_handler)
        assert client.audiences.welcome_sequence.get("aud_123")["active_readers"] == 3
        assert client.audiences.welcome_sequence.update("aud_123", {"enabled": True})["enabled"] is True
        step = client.audiences.welcome_sequence.create_step(
            "aud_123", {"subject": "Welcome", "content_markdown": "# Hi"}
        )
        assert step["id"] == "nwswstp_1"
        client.audiences.welcome_sequence.update_step("aud_123", "nwswstp_1", {"wait_minutes": 0})
        assert client.audiences.welcome_sequence.delete_step("aud_123", "nwswstp_1")["deleted"] is True

    @pytest.mark.asyncio
    async def test_async_calls(self) -> None:
        client = make_async_client(_handler)
        sequence = await client.audiences.welcome_sequence.get("aud_123")
        assert sequence["steps"][0]["wait_minutes"] == 60
        await client.audiences.welcome_sequence.update("aud_123", {"enabled": True})
        await client.audiences.welcome_sequence.create_step(
            "aud_123", {"subject": "Welcome", "content_markdown": "# Hi"}
        )
        await client.audiences.welcome_sequence.update_step("aud_123", "nwswstp_1", {"wait_minutes": 0})
        deleted = await client.audiences.welcome_sequence.delete_step("aud_123", "nwswstp_1")
        assert deleted["deleted"] is True
