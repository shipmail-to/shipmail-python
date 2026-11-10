from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_audience = {
    "object": "audience",
    "id": "aud_123",
    "name": "Newsletter",
    "description": None,
    "member_count": 0,
    "subscribed_count": 0,
    "consent_source": "Signup form",
    "feed_enabled": False,
    "feed_url": None,
    "view_in_browser_default": True,
    "cleanup_enabled": True,
    "cleanup_ignored_issues": 6,
    "cleanup_inactive_days": 180,
    "confirmation_email_copy": None,
    "last_chance_email_copy": None,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z",
}

mock_feed = {
    "object": "audience_feed",
    "audience_id": "aud_123",
    "enabled": True,
    "title": "Newsletter",
    "subtitle": None,
    "site_url": "https://example.com/",
    "canonical_url": "https://example.com/feed.xml",
    "author_name": None,
    "icon_url": None,
    "entry_limit": 25,
    "url": "https://shipmail.to/f/audfeed_test/feed.xml",
    "updated_at": "2026-01-01T00:00:00Z",
}

mock_subscriber = {
    "object": "subscriber",
    "id": "audmem_1",
    "audience_id": "aud_123",
    "email_address": "jane@shipmail.to",
    "display_name": None,
    "status": "subscribed",
    "mailable": True,
    "not_mailable_reasons": [],
    "merge_fields": {},
    "consent_source": "Signup form",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z",
}


mock_confirmation_resend = {
    "object": "confirmation_resend",
    "audience_id": "aud_123",
    "sent": 1,
    "failed": 0,
    "skipped": {"not_found": 0, "not_pending": 0, "too_old": 0, "resend_limit": 0, "recently_sent": 0},
    "remaining": 0,
}


class TestAudiences:
    def test_create_sends_post_with_consent_source(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/audiences"
            assert json.loads(request.content) == {"name": "Newsletter", "consent_source": "Signup form"}
            return json_response(mock_audience, 201)

        client = make_client(handler)
        audience = client.audiences.create({"name": "Newsletter", "consent_source": "Signup form"})
        assert audience["id"] == "aud_123"

    def test_list_sends_get(self) -> None:
        response = {"data": [mock_audience], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/audiences"
            return json_response(response)

        client = make_client(handler)
        result = client.audiences.list()
        assert result["data"][0]["id"] == "aud_123"

    def test_update_sends_patch(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/audiences/aud_123"
            assert json.loads(request.content) == {"name": "Renamed"}
            return json_response({**mock_audience, "name": "Renamed"})

        client = make_client(handler)
        audience = client.audiences.update("aud_123", {"name": "Renamed"})
        assert audience["name"] == "Renamed"

    def test_update_sends_view_in_browser_default(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {"view_in_browser_default": False}
            return json_response({**mock_audience, "view_in_browser_default": False})

        client = make_client(handler)
        audience = client.audiences.update("aud_123", {"view_in_browser_default": False})
        assert audience["view_in_browser_default"] is False

    def test_update_sends_email_copy_and_null_to_clear(self) -> None:
        confirmation = {"fr": {"subject": "Confirmez votre inscription", "message": "Un clic et c'est fait."}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {
                "confirmation_email_copy": confirmation,
                "last_chance_email_copy": None,
            }
            return json_response({**mock_audience, "confirmation_email_copy": confirmation})

        client = make_client(handler)
        audience = client.audiences.update(
            "aud_123",
            {"confirmation_email_copy": confirmation, "last_chance_email_copy": None},
        )
        assert audience["confirmation_email_copy"] == confirmation
        assert audience["last_chance_email_copy"] is None

    def test_delete_returns_none(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/audiences/aud_123"
            return httpx.Response(204)

        client = make_client(handler)
        assert client.audiences.delete("aud_123") is None


class TestSubscribers:
    def test_add_returns_outcome(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/audiences/aud_123/subscribers"
            assert json.loads(request.content) == {"email_address": "jane@shipmail.to"}
            return json_response({"email_address": "jane@shipmail.to", "outcome": "created"})

        client = make_client(handler)
        result = client.audiences.subscribers.add("aud_123", {"email_address": "jane@shipmail.to"})
        assert result["outcome"] == "created"

    def test_add_batch_returns_results(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/audiences/aud_123/subscribers/batch"
            return json_response({"results": [{"email_address": "jane@shipmail.to", "outcome": "created"}]})

        client = make_client(handler)
        result = client.audiences.subscribers.add_batch(
            "aud_123", {"subscribers": [{"email_address": "jane@shipmail.to"}]}
        )
        assert len(result["results"]) == 1

    def test_list_forwards_status_filter(self) -> None:
        response = {"data": [mock_subscriber], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/audiences/aud_123/subscribers"
            assert str(request.url.params.get("status")) == "subscribed"
            return json_response(response)

        client = make_client(handler)
        client.audiences.subscribers.list("aud_123", {"status": "subscribed"})

    def test_add_returns_the_skip_reason(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(
                {"email_address": "jane@shipmail.to", "outcome": "skipped_not_mailable", "reason": "unsubscribed"}
            )

        client = make_client(handler)
        result = client.audiences.subscribers.add("aud_123", {"email_address": "jane@shipmail.to"})
        assert result["outcome"] == "skipped_not_mailable"
        assert result.get("reason") == "unsubscribed"

    def test_get_returns_why_an_address_is_not_mailable(self) -> None:
        reasons = [
            {
                "reason": "unsubscribed",
                "source": "newsletter_optout",
                "created_at": "2026-01-02T00:00:00.000Z",
                "newsletter_id": "nws_1",
                "test_send": False,
            },
            {
                "reason": "hard_bounce",
                "source": "suppression",
                "created_at": "2026-01-01T00:00:00.000Z",
                "expires_at": None,
            },
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/audiences/aud_123/subscribers/audmem_1"
            return json_response({**mock_subscriber, "mailable": False, "not_mailable_reasons": reasons})

        client = make_client(handler)
        subscriber = client.audiences.subscribers.get("aud_123", "audmem_1")
        assert subscriber["status"] == "subscribed"
        assert subscriber["mailable"] is False
        first = subscriber["not_mailable_reasons"][0]
        assert first["source"] == "newsletter_optout"
        assert first["newsletter_id"] == "nws_1"
        assert subscriber["not_mailable_reasons"][1]["source"] == "suppression"

    def test_get_by_email_encodes_segment(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert "/v1/audiences/aud_123/subscribers/by-email/jane%40shipmail.to" in str(request.url)
            return json_response(mock_subscriber)

        client = make_client(handler)
        subscriber = client.audiences.subscribers.get_by_email("aud_123", "jane@shipmail.to")
        assert subscriber["email_address"] == "jane@shipmail.to"

    def test_unsubscribe_sends_post(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/audiences/aud_123/subscribers/audmem_1/unsubscribe"
            return json_response({**mock_subscriber, "status": "unsubscribed"})

        client = make_client(handler)
        subscriber = client.audiences.subscribers.unsubscribe("aud_123", "audmem_1")
        assert subscriber["status"] == "unsubscribed"

    def test_resubscribe_sends_post_with_consent_source(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/audiences/aud_123/subscribers/audmem_1/resubscribe"
            assert json.loads(request.content) == {"consent_source": "Signup form"}
            return json_response({**mock_subscriber, "status": "subscribed"})

        client = make_client(handler)
        subscriber = client.audiences.subscribers.resubscribe(
            "aud_123", "audmem_1", {"consent_source": "Signup form"}
        )
        assert subscriber["status"] == "subscribed"

    def test_resend_confirmation_sends_post_with_subscriber_ids(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/audiences/aud_123/subscribers/resend-confirmation"
            assert json.loads(request.content) == {"subscriber_ids": ["audmem_1"]}
            return json_response(mock_confirmation_resend)

        client = make_client(handler)
        result = client.audiences.subscribers.resend_confirmation("aud_123", {"subscriber_ids": ["audmem_1"]})
        assert result["sent"] == 1
        assert result["skipped"]["too_old"] == 0

    def test_resend_confirmation_without_params_sends_empty_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {}
            return json_response(mock_confirmation_resend)

        client = make_client(handler)
        assert client.audiences.subscribers.resend_confirmation("aud_123")["object"] == "confirmation_resend"

    def test_remove_returns_none(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/audiences/aud_123/subscribers/audmem_1"
            return httpx.Response(204)

        client = make_client(handler)
        assert client.audiences.subscribers.remove("aud_123", "audmem_1") is None


class TestAudienceFeeds:
    def test_get_sends_get(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/audiences/aud_123/feed"
            return json_response(mock_feed)

        client = make_client(handler)
        feed = client.audiences.feeds.get("aud_123")
        assert feed["enabled"] is True
        assert feed["canonical_url"] == "https://example.com/feed.xml"
        assert feed["entry_limit"] == 25

    def test_update_sends_patch(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/audiences/aud_123/feed"
            assert json.loads(request.content) == {
                "title": "Release notes",
                "canonical_url": None,
                "entry_limit": None,
            }
            return json_response(
                {
                    **mock_feed,
                    "title": "Release notes",
                    "canonical_url": None,
                    "entry_limit": None,
                }
            )

        client = make_client(handler)
        feed = client.audiences.feeds.update(
            "aud_123",
            {
                "title": "Release notes",
                "canonical_url": None,
                "entry_limit": None,
            },
        )
        assert feed["title"] == "Release notes"
        assert feed["canonical_url"] is None
        assert feed["entry_limit"] is None

    def test_rotate_and_revoke_send_post(self) -> None:
        paths: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            paths.append(request.url.path)
            return json_response(mock_feed)

        client = make_client(handler)
        client.audiences.feeds.rotate("aud_123")
        client.audiences.feeds.revoke("aud_123")
        assert paths == [
            "/v1/audiences/aud_123/feed/rotate",
            "/v1/audiences/aud_123/feed/revoke",
        ]


class TestAsyncAudiences:
    @pytest.mark.asyncio
    async def test_update_sends_email_copy(self) -> None:
        last_chance = {"en": {"subject": "Still with us?", "message": "Keep getting our letters."}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert json.loads(request.content) == {"last_chance_email_copy": last_chance}
            return json_response({**mock_audience, "last_chance_email_copy": last_chance})

        client = make_async_client(handler)
        audience = await client.audiences.update("aud_123", {"last_chance_email_copy": last_chance})
        await client.aclose()
        assert audience["last_chance_email_copy"] == last_chance


    @pytest.mark.asyncio
    async def test_update_sends_view_in_browser_default(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {"view_in_browser_default": False}
            return json_response({**mock_audience, "view_in_browser_default": False})

        client = make_async_client(handler)
        audience = await client.audiences.update("aud_123", {"view_in_browser_default": False})
        await client.aclose()
        assert audience["view_in_browser_default"] is False


class TestAsyncSubscribers:
    @pytest.mark.asyncio
    async def test_resend_confirmation_sends_post(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/audiences/aud_123/subscribers/resend-confirmation"
            assert json.loads(request.content) == {}
            return json_response(mock_confirmation_resend)

        client = make_async_client(handler)
        result = await client.audiences.subscribers.resend_confirmation("aud_123")
        await client.aclose()
        assert result["remaining"] == 0


class TestAsyncAudienceFeeds:
    @pytest.mark.asyncio
    async def test_get_and_update_preserve_feed_settings(self) -> None:
        requests: list[tuple[str, str, object | None]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content) if request.content else None
            requests.append((request.method, request.url.path, body))
            if request.method == "PATCH":
                return json_response({**mock_feed, **body})
            return json_response(mock_feed)

        client = make_async_client(handler)
        feed = await client.audiences.feeds.get("aud_123")
        updated = await client.audiences.feeds.update(
            "aud_123",
            {
                "canonical_url": "https://publisher.example/feed.xml",
                "entry_limit": 40,
            },
        )
        await client.aclose()

        assert feed["canonical_url"] == "https://example.com/feed.xml"
        assert feed["entry_limit"] == 25
        assert updated["canonical_url"] == "https://publisher.example/feed.xml"
        assert updated["entry_limit"] == 40
        assert requests == [
            ("GET", "/v1/audiences/aud_123/feed", None),
            (
                "PATCH",
                "/v1/audiences/aud_123/feed",
                {
                    "canonical_url": "https://publisher.example/feed.xml",
                    "entry_limit": 40,
                },
            ),
        ]
