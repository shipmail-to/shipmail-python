from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_credential = {
    "object": "smtp_credential",
    "id": "smtpc_0123456789abcdefghjkmnpq",
    "from": "notifications@notify.example.com",
    "name": "Supabase Auth",
    "username": "smtp-smtpc_0123456789abcdefghjkmnpq@txsmtp.shipmail.to",
    "host": "mx1.shipmail.to",
    "ports": [{"port": 465, "security": "tls"}, {"port": 587, "security": "starttls"}],
    "last_used_at": None,
    "created_at": "2026-11-03T00:00:00.000Z",
}


class TestList:
    def test_lists_all_credentials(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/smtp-credentials"
            assert "from" not in request.url.params
            return json_response({"object": "list", "data": [mock_credential]})

        result = make_client(handler).smtp_credentials.list()
        assert result["data"][0]["id"] == mock_credential["id"]

    @pytest.mark.asyncio
    async def test_async_filters_by_sender(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["from"] == "notifications@notify.example.com"
            return json_response({"object": "list", "data": [mock_credential]})

        client = make_async_client(handler)
        result = await client.smtp_credentials.list({"from": "notifications@notify.example.com"})
        assert len(result["data"]) == 1


class TestCreate:
    def test_creates_without_idempotency_key(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/smtp-credentials"
            assert "idempotency-key" not in request.headers
            assert json.loads(request.content) == {
                "from": "notifications@notify.example.com",
                "name": "Supabase Auth",
            }
            return json_response({**mock_credential, "password": "shown-once"}, 201)

        result = make_client(handler).smtp_credentials.create(
            {"from": "notifications@notify.example.com", "name": "Supabase Auth"}
        )
        assert result["password"] == "shown-once"

    @pytest.mark.asyncio
    async def test_async_creates(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            return json_response({**mock_credential, "password": "shown-once"}, 201)

        client = make_async_client(handler)
        result = await client.smtp_credentials.create(
            {"from": "notifications@notify.example.com", "name": "Supabase Auth"}
        )
        assert result["ports"][1]["port"] == 587


class TestRevoke:
    def test_revokes_by_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/smtp-credentials/smtpc_0123456789abcdefghjkmnpq"
            return httpx.Response(204)

        make_client(handler).smtp_credentials.revoke("smtpc_0123456789abcdefghjkmnpq")

    @pytest.mark.asyncio
    async def test_async_revokes_by_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            return httpx.Response(204)

        await make_async_client(handler).smtp_credentials.revoke("smtpc_0123456789abcdefghjkmnpq")
