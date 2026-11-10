from __future__ import annotations

import json
from typing import get_args

import httpx
import pytest

from shipmail import NewsletterStatus
from tests.conftest import json_response, make_async_client, make_client

mock_newsletter = {
    "object": "newsletter",
    "id": "nws_123",
    "audience_id": "aud_123",
    "sender_identity_id": "nwsid_123",
    "newsletter_domain_id": "nwsdom_123",
    "name": "July changelog",
    "subject": "What shipped in July",
    "preview_text": "A quick product update",
    "from_name": "Shipmail",
    "from_address": "updates@example.com",
    "reply_to_address": None,
    "body_html": "<p>Hello</p>",
    "body_text": "Hello",
    "status": "draft",
    "archive_visibility": "private",
    "view_in_browser": True,
    "feed_entry_url": None,
    "styling_mode": "styled",
    "track_engagement": False,
    "add_utm_tags": False,
    "opened_count": None,
    "clicked_count": None,
    "send_limit": None,
    "held_count": 0,
    "subject_b": None,
    "subject_test_percent": None,
    "subject_test_hours": None,
    "subject_test_winner": None,
    "subject_test_decided_at": None,
    "preflight_status": "not_run",
    "preflight_results": {},
    "send_window_hours": 6,
    "send_rate_per_hour": 500,
    "recipient_count": 0,
    "sent_count": 0,
    "delivered_count": 0,
    "bounced_count": 0,
    "complained_count": 0,
    "failed_count": 0,
    "skipped_count": 0,
    "scheduled_at": None,
    "approved_at": None,
    "started_at": None,
    "completed_at": None,
    "cancelled_at": None,
    "created_at": "2026-07-01T00:00:00Z",
    "updated_at": "2026-07-01T00:00:00Z",
}


def test_newsletter_status_includes_in_review() -> None:
    assert "in_review" in get_args(NewsletterStatus)

mock_newsletter_domain = {
    "object": "newsletter_domain",
    "id": "nwsdom_123",
    "root_domain_name": "example.com",
    "domain_name": "updates.example.com",
    "from_local_part": "updates",
    "from_address": "updates@updates.example.com",
    "mail_from_domain": "mail.updates.example.com",
    "reply_to_address": "hello@example.com",
    "status": "verified",
    "dkim_status": "verified",
    "mail_from_status": "verified",
    "spf_status": "verified",
    "dmarc_status": "verified",
    "verified_at": "2026-07-01T00:00:00Z",
    "created_at": "2026-07-01T00:00:00Z",
    "updated_at": "2026-07-01T00:00:00Z",
}

mock_newsletter_sender_identity = {
    "object": "newsletter_sender_identity",
    "id": "nwsid_123",
    "newsletter_domain_id": "nwsdom_123",
    "from_name": "Shipmail",
    "from_address": "updates@updates.example.com",
    "business_name": "Shipmail, Inc.",
    "postal_address": "123 Market St",
    "footer_text": "You subscribed at shipmail.to.",
    "domain_status": "verified",
    "is_default": True,
    "created_at": "2026-07-01T00:00:00Z",
    "updated_at": "2026-07-01T00:00:00Z",
}

mock_newsletter_asset = {
    "object": "newsletter_asset",
    "id": "nwsasset_123",
    "kind": "image",
    "filename": "hero.png",
    "content_type": "image/png",
    "byte_size": 1024,
    "checksum_sha256": "a" * 64,
    "url": "https://cdn.shipmail.to/newsletter-images/org_123/hero.png",
    "image_url": "https://cdn.shipmail.to/newsletter-images/org_123/hero.png",
    "video_url": None,
    "thumbnail_url": None,
    "thumbnail_content_type": None,
    "thumbnail_byte_size": None,
    "duration_seconds": None,
    "width": 1200,
    "height": 630,
    "created_at": "2026-07-01T00:00:00Z",
}


class TestNewsletters:
    def test_create_sends_post_with_blocks(self) -> None:
        blocks = [
            {"type": "heading", "level": 1, "text": "July updates"},
            {
                "type": "paragraph",
                "body": '<p>Read the <a href="https://example.com/launch">launch notes</a>.</p>',
            },
            {"type": "list", "ordered": False, "items": ["One", "<strong>Two</strong>"]},
            {
                "type": "callout",
                "variant": "info",
                "title": "Quick note",
                "body": "A <em>short</em> intro.",
            },
            {
                "type": "columns",
                "ratio": "50-50",
                "left": {"title": "For teams", "body": "Shared inbox improvements."},
                "right": {"title": "For agents", "body": "API and MCP improvements."},
            },
        ]

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/newsletters"
            assert json.loads(request.content) == {
                "audience_id": "aud_123",
                "sender_identity_id": "nwsid_123",
                "name": "July changelog",
                "subject": "What shipped in July",
                "styling_mode": "plain",
                "blocks": blocks,
            }
            return json_response(mock_newsletter, 201)

        client = make_client(handler)
        newsletter = client.newsletters.create(
            {
                "audience_id": "aud_123",
                "sender_identity_id": "nwsid_123",
                "name": "July changelog",
                "subject": "What shipped in July",
                "styling_mode": "plain",
                "blocks": blocks,
            }
        )
        assert newsletter["id"] == "nws_123"

    def test_create_from_changelog_sends_styling_mode(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/newsletters/from-changelog"
            assert json.loads(request.content) == {
                "audience_id": "aud_123",
                "sender_identity_id": "nwsid_123",
                "name": "July changelog",
                "subject": "What shipped in July",
                "entries": [{"title": "Plain update"}],
                "styling_mode": "plain",
            }
            return json_response(mock_newsletter, 201)

        client = make_client(handler)
        newsletter = client.newsletters.create_from_changelog(
            {
                "audience_id": "aud_123",
                "sender_identity_id": "nwsid_123",
                "name": "July changelog",
                "subject": "What shipped in July",
                "entries": [{"title": "Plain update"}],
                "styling_mode": "plain",
            }
        )
        assert newsletter["styling_mode"] == "styled"

    def test_create_sends_post_with_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/newsletters"
            assert json.loads(request.content) == {
                "audience_id": "aud_123",
                "sender_identity_id": "nwsid_123",
                "name": "July changelog",
                "subject": "What shipped in July",
                "body_html": "<p>Hello</p>",
            }
            return json_response(mock_newsletter, 201)

        client = make_client(handler)
        newsletter = client.newsletters.create(
            {
                "audience_id": "aud_123",
                "sender_identity_id": "nwsid_123",
                "name": "July changelog",
                "subject": "What shipped in July",
                "body_html": "<p>Hello</p>",
            }
        )
        assert newsletter["id"] == "nws_123"

    def test_list_sends_get(self) -> None:
        response = {"data": [mock_newsletter], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/newsletters"
            return json_response(response)

        client = make_client(handler)
        result = client.newsletters.list()
        assert result["data"][0]["id"] == "nws_123"

    def test_domains_list_sends_get(self) -> None:
        response = {"data": [mock_newsletter_domain], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/newsletter-domains"
            assert request.url.params.get("limit") == "10"
            return json_response(response)

        client = make_client(handler)
        result = client.newsletters.domains.list({"limit": 10})
        assert result["data"][0]["id"] == "nwsdom_123"

    def test_sender_identities_list_sends_get(self) -> None:
        response = {
            "data": [mock_newsletter_sender_identity],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/newsletter-sender-identities"
            assert request.url.params.get("limit") == "10"
            return json_response(response)

        client = make_client(handler)
        result = client.newsletters.sender_identities.list({"limit": 10})
        assert result["data"][0]["id"] == "nwsid_123"

    def test_domain_setup_reaches_create_verify_and_delete(self) -> None:
        calls: list[tuple[str, str, object]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content) if request.content else None
            calls.append((request.method, request.url.path, body))
            if request.method == "DELETE":
                return httpx.Response(204)
            return json_response(mock_newsletter_domain)

        client = make_client(handler)
        client.newsletters.domains.create(
            {"root_domain": "example.com", "reply_to_address": "hello@example.com"}
        )
        client.newsletters.domains.verify("nwsdom_123")
        client.newsletters.domains.delete("nwsdom_123")
        assert calls == [
            (
                "POST",
                "/v1/newsletter-domains",
                {"root_domain": "example.com", "reply_to_address": "hello@example.com"},
            ),
            ("POST", "/v1/newsletter-domains/nwsdom_123/verify", None),
            ("DELETE", "/v1/newsletter-domains/nwsdom_123", None),
        ]

    def test_sender_identity_writes(self) -> None:
        calls: list[tuple[str, str, object]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content) if request.content else None
            calls.append((request.method, request.url.path, body))
            if request.method == "DELETE":
                return httpx.Response(204)
            return json_response(mock_newsletter_sender_identity)

        client = make_client(handler)
        client.newsletters.sender_identities.create(
            {"newsletter_domain_id": "nwsdom_123", "from_name": "Acme", "business_name": "Acme Ltd."}
        )
        client.newsletters.sender_identities.update("nwsid_123", {"make_default": True})
        assert client.newsletters.sender_identities.delete("nwsid_123") is None
        assert [call[:2] for call in calls] == [
            ("POST", "/v1/newsletter-sender-identities"),
            ("PATCH", "/v1/newsletter-sender-identities/nwsid_123"),
            ("DELETE", "/v1/newsletter-sender-identities/nwsid_123"),
        ]
        assert calls[1][2] == {"make_default": True}

    @pytest.mark.asyncio
    async def test_async_domain_setup(self) -> None:
        paths: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            paths.append((request.method, request.url.path))
            if request.method == "DELETE":
                return httpx.Response(204)
            if "sender-identities" in request.url.path:
                return json_response(mock_newsletter_sender_identity)
            return json_response(mock_newsletter_domain)

        client = make_async_client(handler)
        domain = await client.newsletters.domains.create(
            {"root_domain": "example.com", "reply_to_address": "hello@example.com"}
        )
        await client.newsletters.domains.verify(domain["id"])
        await client.newsletters.sender_identities.create(
            {"newsletter_domain_id": domain["id"], "from_name": "Acme", "business_name": "Acme Ltd."}
        )
        await client.newsletters.sender_identities.update("nwsid_123", {"from_name": "Acme News"})
        await client.newsletters.sender_identities.delete("nwsid_123")
        await client.newsletters.domains.delete(domain["id"])
        assert paths == [
            ("POST", "/v1/newsletter-domains"),
            ("POST", "/v1/newsletter-domains/nwsdom_123/verify"),
            ("POST", "/v1/newsletter-sender-identities"),
            ("PATCH", "/v1/newsletter-sender-identities/nwsid_123"),
            ("DELETE", "/v1/newsletter-sender-identities/nwsid_123"),
            ("DELETE", "/v1/newsletter-domains/nwsdom_123"),
        ]

    def test_assets_list_sends_filters_and_cursor(self) -> None:
        response = {
            "data": [mock_newsletter_asset],
            "pagination": {"next_cursor": "next-page", "has_more": True, "limit": 25},
            "storage": {
                "used_bytes": 1024,
                "limit_bytes": None,
                "remaining_bytes": None,
                "over_limit": False,
                "plan": "free",
                "is_in_trial": False,
                "next_upgrade": None,
            },
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/newsletter-assets"
            assert request.url.params.get("kind") == "image"
            assert request.url.params.get("q") == "hero"
            assert request.url.params.get("limit") == "25"
            assert request.url.params.get("cursor") == "current-page"
            return json_response(response)

        client = make_client(handler)
        result = client.newsletters.assets.list(
            {"kind": "image", "q": "hero", "limit": 25, "cursor": "current-page"}
        )
        assert result["data"][0]["id"] == "nwsasset_123"
        assert result["pagination"]["next_cursor"] == "next-page"
        assert result["storage"]["limit_bytes"] is None

    def test_prepare_asset_upload_sends_post(self) -> None:
        response = {
            "object": "newsletter_asset_upload",
            "kind": "image",
            "filename": "hero.png",
            "content_type": "image/png",
            "size": 123,
            "sha256": "a" * 64,
            "upload_url": "https://r2.example/newsletter-images/org_123/token.png?signed=put",
            "upload_method": "PUT",
            "upload_headers": {
                "Content-Type": "image/png",
                "If-None-Match": "*",
            },
            "complete_url": "https://shipmail.to/api/v1/newsletter-asset-uploads/token",
            "complete_method": "POST",
            "expires_at": "2026-08-08T12:05:00.000Z",
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/newsletter-assets/upload-tokens"
            assert json.loads(request.content) == {
                "filename": "hero.png",
                "content_type": "image/png",
                "size": 123,
                "sha256": "a" * 64,
            }
            return json_response(response, 201)

        client = make_client(handler)
        prepared = client.newsletters.assets.prepare_upload(
            {
                "filename": "hero.png",
                "content_type": "image/png",
                "size": 123,
                "sha256": "a" * 64,
            }
        )
        assert prepared["upload_method"] == "PUT"
        assert prepared["complete_method"] == "POST"

    def test_update_sends_patch(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/newsletters/nws_123"
            assert json.loads(request.content) == {
                "subject": "Updated",
                "feed_entry_url": "https://example.com/",
                "styling_mode": "plain",
                "track_engagement": True,
                "add_utm_tags": True,
                "view_in_browser": False,
            }
            return json_response(
                {
                    **mock_newsletter,
                    "subject": "Updated",
                    "track_engagement": True,
                    "add_utm_tags": True,
                    "view_in_browser": False,
                    "opened_count": 12,
                    "clicked_count": 4,
                }
            )

        client = make_client(handler)
        newsletter = client.newsletters.update(
            "nws_123",
            {
                "subject": "Updated",
                "feed_entry_url": "https://example.com/",
                "styling_mode": "plain",
                "track_engagement": True,
                "add_utm_tags": True,
                "view_in_browser": False,
            },
        )
        assert newsletter["subject"] == "Updated"
        assert newsletter["view_in_browser"] is False
        assert newsletter["track_engagement"] is True
        assert newsletter["add_utm_tags"] is True
        assert newsletter["opened_count"] == 12
        assert newsletter["clicked_count"] == 4

    def test_preflight_sends_post(self) -> None:
        response = {"object": "newsletter_preflight", "newsletter_id": "nws_123", "status": "passed", "items": []}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/newsletters/nws_123/preflight"
            return json_response(response)

        client = make_client(handler)
        result = client.newsletters.preflight("nws_123")
        assert result["status"] == "passed"

    def test_send_test_sends_post(self) -> None:
        response = {
            "object": "newsletter_test_send",
            "id": "nwstest_123",
            "newsletter_id": "nws_123",
            "message_id": "msg_123",
            "recipient_email": "owner@example.com",
            "status": "sent",
            "last_error": None,
            "sent_at": "2026-07-01T00:00:00Z",
            "created_at": "2026-07-01T00:00:00Z",
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/newsletters/nws_123/test-send"
            assert json.loads(request.content) == {"recipient_email": "owner@example.com"}
            return json_response(response, 201)

        client = make_client(handler)
        result = client.newsletters.send_test("nws_123", {"recipient_email": "owner@example.com"})
        assert result["status"] == "sent"

    def test_schedule_sends_post(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/newsletters/nws_123/schedule"
            assert json.loads(request.content) == {"scheduled_at": "2026-08-01T09:00:00Z"}
            return json_response({**mock_newsletter, "status": "scheduled"})

        client = make_client(handler)
        newsletter = client.newsletters.schedule("nws_123", {"scheduled_at": "2026-08-01T09:00:00Z"})
        assert newsletter["status"] == "scheduled"

    def test_cancel_and_resume_post_to_lifecycle_endpoints(self) -> None:
        paths: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            paths.append(request.url.path)
            return json_response(mock_newsletter)

        client = make_client(handler)
        client.newsletters.cancel("nws_123")
        client.newsletters.resume("nws_123")
        assert paths == ["/v1/newsletters/nws_123/cancel", "/v1/newsletters/nws_123/resume"]

    def test_schedule_with_limit_and_send_to_more(self) -> None:
        calls: list[tuple[str, object]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            calls.append((request.url.path, json.loads(request.content)))
            return json_response({**mock_newsletter, "status": "sending", "send_limit": 500})

        client = make_client(handler)
        client.newsletters.schedule("nws_123", {"scheduled_at": "2026-08-01T09:00:00Z", "limit": 500})
        client.newsletters.send_to_more("nws_123", {"count": 1000})
        client.newsletters.send_to_more("nws_123")
        assert calls == [
            ("/v1/newsletters/nws_123/schedule", {"scheduled_at": "2026-08-01T09:00:00Z", "limit": 500}),
            ("/v1/newsletters/nws_123/send-more", {"count": 1000}),
            ("/v1/newsletters/nws_123/send-more", {}),
        ]


class TestAsyncNewsletters:
    @pytest.mark.asyncio
    async def test_send_to_more_posts_the_count(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/newsletters/nws_123/send-more"
            assert json.loads(request.content) == {"count": 5}
            return json_response(mock_newsletter)

        client = make_async_client(handler)
        await client.newsletters.send_to_more("nws_123", {"count": 5})

    @pytest.mark.asyncio
    async def test_create_and_update_send_rich_block_prose(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return json_response(mock_newsletter, 201 if request.method == "POST" else 200)

        client = make_async_client(handler)
        await client.newsletters.create(
            {
                "audience_id": "aud_123",
                "sender_identity_id": "nwsid_123",
                "name": "Plain note",
                "subject": "Hello",
                "blocks": [
                    {
                        "type": "paragraph",
                        "body": '<a href="https://example.com/create">Create link</a>',
                    }
                ],
                "styling_mode": "plain",
                "add_utm_tags": True,
                "view_in_browser": False,
            }
        )
        await client.newsletters.update(
            "nws_123",
            {
                "blocks": [
                    {
                        "type": "callout",
                        "body": '<strong>Updated</strong> with <a href="https://example.com/update">a link</a>.',
                    }
                ],
                "styling_mode": "styled",
                "add_utm_tags": False,
                "view_in_browser": True,
            },
        )
        await client.aclose()

        assert [request.method for request in requests] == ["POST", "PATCH"]
        payloads = [json.loads(request.content) for request in requests]
        assert payloads[0]["blocks"][0]["body"] == '<a href="https://example.com/create">Create link</a>'
        assert payloads[1]["blocks"][0]["body"] == (
            '<strong>Updated</strong> with <a href="https://example.com/update">a link</a>.'
        )
        assert [payload["styling_mode"] for payload in payloads] == ["plain", "styled"]
        assert [payload["add_utm_tags"] for payload in payloads] == [True, False]
        assert [payload["view_in_browser"] for payload in payloads] == [False, True]


mock_newsletter_recipient = {
    "object": "newsletter_recipient",
    "id": "nwsrcp_1",
    "newsletter_id": "nws_123",
    "email_address": "reader@example.com",
    "status": "skipped",
    "reason": "opted_out",
    "subscriber_id": "audmem_1",
    "sent_at": None,
    "delivered_at": None,
    "bounced_at": None,
    "complained_at": None,
    "unsubscribed_at": None,
    "created_at": "2026-07-01T00:00:00Z",
}

mock_newsletter_preview = {
    "object": "newsletter_preview",
    "newsletter_id": "nws_123",
    "subject": "What shipped in July, Jane",
    "html": "<p>Hello Jane</p>",
    "archive_html": "<p>Hello</p>",
    "text": "Hello Jane",
    "headers": {
        "List-Unsubscribe": "<https://shipmail.to/unsubscribe/token>",
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
    },
    "warnings": [],
    "url_breakdown": {"total": 0, "counted": [], "ignored": []},
}


class TestNewsletterConsent:
    def test_preview_defaults_to_an_empty_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/newsletters/nws_123/preview"
            assert json.loads(request.content) == {}
            return json_response(mock_newsletter_preview)

        client = make_client(handler)
        preview = client.newsletters.preview("nws_123")
        assert preview["subject"] == "What shipped in July, Jane"
        assert preview["headers"]["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"

    def test_preview_as_a_subscriber_sends_preview_as(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {
                "preview_as": {"type": "subscriber", "subscriber_id": "audmem_1"}
            }
            return json_response(mock_newsletter_preview)

        client = make_client(handler)
        client.newsletters.preview(
            "nws_123", {"preview_as": {"type": "subscriber", "subscriber_id": "audmem_1"}}
        )

    def test_domain_and_sender_identity_get(self) -> None:
        paths: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            paths.append((request.method, request.url.path))
            if "sender-identities" in request.url.path:
                return json_response(mock_newsletter_sender_identity)
            return json_response(mock_newsletter_domain)

        client = make_client(handler)
        domain = client.newsletters.domains.get("nwsdom_123")
        identity = client.newsletters.sender_identities.get("nwsid_123")
        assert domain["object"] == "newsletter_domain"
        assert identity["object"] == "newsletter_sender_identity"
        assert paths == [
            ("GET", "/v1/newsletter-domains/nwsdom_123"),
            ("GET", "/v1/newsletter-sender-identities/nwsid_123"),
        ]

    def test_sender_identity_create_sends_make_default_false(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content)["make_default"] is False
            return json_response({**mock_newsletter_sender_identity, "is_default": False})

        client = make_client(handler)
        identity = client.newsletters.sender_identities.create(
            {
                "newsletter_domain_id": "nwsdom_123",
                "from_name": "Acme",
                "business_name": "Acme Ltd.",
                "make_default": False,
            }
        )
        assert identity["is_default"] is False

    def test_recipients_list_forwards_filters(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/newsletters/nws_123/recipients"
            assert dict(request.url.params) == {
                "cursor": "c1",
                "limit": "10",
                "status": "skipped",
                "reason": "opted_out",
            }
            return json_response(
                {"data": [mock_newsletter_recipient], "pagination": {"next_cursor": None, "has_more": False}}
            )

        client = make_client(handler)
        result = client.newsletters.recipients.list(
            "nws_123", {"cursor": "c1", "limit": 10, "status": "skipped", "reason": "opted_out"}
        )
        assert result["data"][0]["reason"] == "opted_out"

    def test_recipients_auto_paginate_follow_the_cursor(self) -> None:
        cursors: list[str | None] = []

        def handler(request: httpx.Request) -> httpx.Response:
            cursor = request.url.params.get("cursor")
            cursors.append(cursor)
            assert request.url.params.get("status") == "bounced"
            if cursor is None:
                return json_response(
                    {"data": [mock_newsletter_recipient], "pagination": {"next_cursor": "c2", "has_more": True}}
                )
            return json_response(
                {
                    "data": [{**mock_newsletter_recipient, "id": "nwsrcp_2"}],
                    "pagination": {"next_cursor": None, "has_more": False},
                }
            )

        client = make_client(handler)
        ids = [r["id"] for r in client.newsletters.recipients.list_auto_paginating("nws_123", status="bounced")]
        assert ids == ["nwsrcp_1", "nwsrcp_2"]
        assert cursors == [None, "c2"]

    def test_recipient_get_by_email_encodes_the_address(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "/v1/newsletters/nws_123/recipients/by-email/reader%40example.com" in str(request.url)
            return json_response(mock_newsletter_recipient)

        client = make_client(handler)
        recipient = client.newsletters.recipients.get_by_email("nws_123", "reader@example.com")
        assert recipient["status"] == "skipped"


class TestAsyncNewsletterConsent:
    @pytest.mark.asyncio
    async def test_preview_gets_and_recipients(self) -> None:
        calls: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append((request.method, request.url.path))
            path = request.url.path
            if path.endswith("/preview"):
                assert json.loads(request.content) == {"preview_as": {"type": "sample"}}
                return json_response(mock_newsletter_preview)
            if "sender-identities" in path:
                return json_response(mock_newsletter_sender_identity)
            if "newsletter-domains" in path:
                return json_response(mock_newsletter_domain)
            if "/by-email/" in path:
                return json_response(mock_newsletter_recipient)
            return json_response(
                {"data": [mock_newsletter_recipient], "pagination": {"next_cursor": None, "has_more": False}}
            )

        client = make_async_client(handler)
        await client.newsletters.preview("nws_123", {"preview_as": {"type": "sample"}})
        await client.newsletters.domains.get("nwsdom_123")
        await client.newsletters.sender_identities.get("nwsid_123")
        await client.newsletters.recipients.list("nws_123")
        ids = [r["id"] async for r in client.newsletters.recipients.list_auto_paginating("nws_123")]
        await client.newsletters.recipients.get_by_email("nws_123", "reader@example.com")
        assert ids == ["nwsrcp_1"]
        assert calls == [
            ("POST", "/v1/newsletters/nws_123/preview"),
            ("GET", "/v1/newsletter-domains/nwsdom_123"),
            ("GET", "/v1/newsletter-sender-identities/nwsid_123"),
            ("GET", "/v1/newsletters/nws_123/recipients"),
            ("GET", "/v1/newsletters/nws_123/recipients"),
            ("GET", "/v1/newsletters/nws_123/recipients/by-email/reader@example.com"),
        ]
