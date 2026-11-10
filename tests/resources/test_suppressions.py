from __future__ import annotations

from urllib.parse import quote

import json

import httpx
import pytest

from shipmail import ConflictError
from tests.conftest import json_response, make_async_client, make_client

mock_suppression = {
    "object": "suppression",
    "email_address": "bounced@example.com",
    "reason": "hard_bounce",
    "scope": "all",
    "expires_at": None,
    "created_at": "2025-01-01T00:00:00Z",
    "source": "suppression",
}

mock_optout = {
    "object": "suppression",
    "email_address": "reader@example.com",
    "reason": "unsubscribe",
    "scope": "marketing",
    "expires_at": None,
    "created_at": "2025-01-02T00:00:00Z",
    "source": "newsletter_optout",
    "newsletter_id": "nws_1",
    "test_send": False,
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
            assert "reason" not in request.url.params
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

    def test_returns_the_removal_when_an_opt_out_remains(self) -> None:
        removal = {
            "object": "suppression_removal",
            "email_address": "both@example.com",
            "removed": True,
            "newsletter_optout_remains": True,
            "message": "The suppression was removed.",
        }

        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(removal)

        client = make_client(handler)
        result = client.suppressions.remove("both@example.com")
        assert result is not None
        assert result["object"] == "suppression_removal"
        assert result["newsletter_optout_remains"] is True

    def test_raises_conflict_for_an_opt_out_only(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(
                {
                    "error": {
                        "type": "conflict",
                        "message": "This address unsubscribed from your newsletters.",
                        "details": [
                            {"field": "email", "code": "consent_opt_out", "message": "Only a resubscribe removes it."}
                        ],
                    }
                },
                409,
            )

        client = make_client(handler)
        with pytest.raises(ConflictError) as info:
            client.suppressions.remove("reader@example.com")
        assert info.value.status == 409
        assert info.value.details is not None
        assert info.value.details[0].get("code") == "consent_opt_out"

    @pytest.mark.asyncio
    async def test_async_returns_none_or_the_removal(self) -> None:
        statuses = iter([204, 200])

        def handler(request: httpx.Request) -> httpx.Response:
            status = next(statuses)
            if status == 204:
                return httpx.Response(204)
            return json_response(
                {
                    "object": "suppression_removal",
                    "email_address": "both@example.com",
                    "removed": True,
                    "newsletter_optout_remains": True,
                    "message": "Removed.",
                }
            )

        client = make_async_client(handler)
        assert await client.suppressions.remove("bounced@example.com") is None
        result = await client.suppressions.remove("both@example.com")
        assert result is not None
        assert result["removed"] is True


mock_lift = {
    "object": "newsletter_opt_out_lift",
    "email_address": "reader+news@example.com",
    "consent_source": "Asked to rejoin by email",
    "consent_attested_at": "2026-11-09T10:00:00.000Z",
    "opted_out_at": "2026-10-01T08:00:00.000Z",
    "newsletter_id": None,
}


class TestResubscribe:
    def test_posts_the_consent_to_the_encoded_address(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.raw_path == b"/v1/newsletter-opt-outs/reader%2Bnews%40example.com/resubscribe"
            assert json.loads(request.content) == {"consent_source": "Asked to rejoin by email"}
            return json_response(mock_lift)

        client = make_client(handler)
        lift = client.suppressions.resubscribe(
            "reader+news@example.com", {"consent_source": "Asked to rejoin by email"}
        )
        assert lift["object"] == "newsletter_opt_out_lift"
        assert lift["opted_out_at"] == "2026-10-01T08:00:00.000Z"

    def test_raises_conflict_while_a_suppression_blocks(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(
                {"error": {"type": "conflict", "message": "Remove the suppression first."}}, status_code=409
            )

        client = make_client(handler)
        with pytest.raises(ConflictError):
            client.suppressions.resubscribe("bounced@example.com", {"consent_source": "Asked to rejoin"})

    @pytest.mark.asyncio
    async def test_async_posts_the_consent(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/newsletter-opt-outs/reader+news@example.com/resubscribe"
            return json_response(mock_lift)

        client = make_async_client(handler)
        lift = await client.suppressions.resubscribe(
            "reader+news@example.com", {"consent_source": "Asked to rejoin by email"}
        )
        assert lift["consent_source"] == "Asked to rejoin by email"


class TestListEntries:
    def test_lists_opt_outs_with_their_source(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params.get("reason") == "unsubscribe"
            return json_response({"data": [mock_optout], "pagination": {"next_cursor": None, "has_more": False}})

        client = make_client(handler)
        result = client.suppressions.list({"reason": "unsubscribe"})
        entry = result["data"][0]
        assert entry["source"] == "newsletter_optout"
        assert entry["test_send"] is False

    def test_auto_paginating_forwards_reason(self) -> None:
        seen: list[str | None] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(request.url.params.get("reason"))
            return json_response(
                {"data": [mock_suppression, mock_optout], "pagination": {"next_cursor": None, "has_more": False}}
            )

        client = make_client(handler)
        entries = list(client.suppressions.list_auto_paginating(reason="manual"))
        assert seen == ["manual"]
        assert [entry["source"] for entry in entries] == ["suppression", "newsletter_optout"]

    @pytest.mark.asyncio
    async def test_async_list_forwards_reason(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params.get("reason") == "hard_bounce"
            assert request.url.params.get("scope") == "all"
            return json_response({"data": [mock_suppression], "pagination": {"next_cursor": None, "has_more": False}})

        client = make_async_client(handler)
        result = await client.suppressions.list({"reason": "hard_bounce", "scope": "all"})
        assert result["data"][0]["source"] == "suppression"
