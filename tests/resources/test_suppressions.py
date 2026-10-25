from __future__ import annotations

from urllib.parse import quote

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_suppression = {
    "object": "suppression",
    "email_address": "bounced@example.com",
    "reason": "hard_bounce",
    "scope": "all",
    "expires_at": None,
    "created_at": "2025-01-01T00:00:00Z",
}


class TestCreate:
    def test_sends_post_with_the_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/suppressions"
            assert json.loads(request.content) == {"email": "person@example.com", "scope": "marketing"}
            return json_response({**mock_suppression, "email_address": "person@example.com", "reason": "manual"}, 201)

        client = make_client(handler)
        result = client.suppressions.create({"email": "person@example.com", "scope": "marketing"})
        assert result["reason"] == "manual"

    @pytest.mark.asyncio
    async def test_async_sends_post(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert json.loads(request.content) == {"email": "person@example.com"}
            return json_response(mock_suppression, 200)

        client = make_async_client(handler)
        result = await client.suppressions.create({"email": "person@example.com"})
        assert result["email_address"] == "bounced@example.com"


class TestList:
    def test_sends_get_suppressions(self) -> None:
        response = {
            "data": [mock_suppression],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/suppressions"
            return json_response(response)

        client = make_client(handler)
        result = client.suppressions.list()
        assert len(result["data"]) == 1
        assert result["data"][0]["email_address"] == "bounced@example.com"
        assert result["pagination"]["has_more"] is False

    def test_sends_limit_query_param(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url.params.get("limit")) == "10"
            return json_response(response)

        client = make_client(handler)
        client.suppressions.list({"limit": 10})

    def test_sends_scope_query_param(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params.get("scope") == "marketing"
            return json_response(response)

        client = make_client(handler)
        client.suppressions.list({"scope": "marketing"})

    def test_omits_undefined_params(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert "cursor" not in request.url.params
            assert "limit" not in request.url.params
            assert "scope" not in request.url.params
            return json_response(response)

        client = make_client(handler)
        client.suppressions.list()


class TestRemove:
    def test_sends_delete_with_url_encoded_email(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            encoded = quote("bounced@example.com", safe="")
            assert encoded in str(request.url.raw_path.decode())
            return httpx.Response(204)

        client = make_client(handler)
        result = client.suppressions.remove("bounced@example.com")
        assert result is None
