from __future__ import annotations

import json

import httpx

from tests.conftest import json_response, make_client

mock_webhook = {
    "object": "webhook",
    "id": "whk_123",
    "url": "https://example.com/webhooks",
    "events": ["message.received", "message.sent"],
    "active": True,
    "description": "My webhook",
    "mailbox_ids": None,
    "domain_ids": None,
    "has_authorization": False,
    "has_standard_webhooks_secret": False,
    "include_reply_text": False,
    "authenticated_senders_only": False,
    "allowed_senders": None,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}

mock_webhook_with_secret = {
    **mock_webhook,
    "secret": "whsec_abc123",
}

mock_delivery = {
    "object": "webhook_delivery",
    "id": "dlv_001",
    "event_id": "evt_001",
    "event_type": "message.received",
    "status": "delivered",
    "attempts": 1,
    "last_status_code": 200,
    "last_error": None,
    "created_at": "2025-01-01T00:00:00Z",
    "delivered_at": "2025-01-01T00:00:01Z",
}


class TestCreate:
    def test_sends_post_webhooks_with_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/webhooks"
            body = json.loads(request.content)
            assert body == {
                "url": "https://example.com/webhooks",
                "events": ["message.received", "message.sent"],
                "description": "My webhook",
            }
            return json_response(mock_webhook_with_secret)

        client = make_client(handler)
        webhook = client.webhooks.create({
            "url": "https://example.com/webhooks",
            "events": ["message.received", "message.sent"],
            "description": "My webhook",
        })
        assert webhook["id"] == "whk_123"
        assert webhook["secret"] == "whsec_abc123"
        assert webhook["url"] == "https://example.com/webhooks"

    def test_sends_authorization_and_never_receives_it(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {
                "url": "https://example.com/hook",
                "events": ["message.received"],
                "authorization": "Bearer key_123",
            }
            return json_response({**mock_webhook_with_secret, "has_authorization": True})

        client = make_client(handler)
        webhook = client.webhooks.create({
            "url": "https://example.com/hook",
            "events": ["message.received"],
            "authorization": "Bearer key_123",
        })
        assert webhook["has_authorization"] is True
        assert "authorization" not in webhook

    def test_creates_webhook_without_description(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {
                "url": "https://example.com/hook",
                "events": ["message.received"],
            }
            return json_response(mock_webhook_with_secret)

        client = make_client(handler)
        client.webhooks.create({
            "url": "https://example.com/hook",
            "events": ["message.received"],
        })


class TestList:
    def test_sends_get_webhooks(self) -> None:
        response = {
            "data": [mock_webhook],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/webhooks"
            return json_response(response)

        client = make_client(handler)
        result = client.webhooks.list()
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == "whk_123"

    def test_sends_cursor_and_limit(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url.params.get("cursor")) == "cur_abc"
            assert str(request.url.params.get("limit")) == "50"
            return json_response(response)

        client = make_client(handler)
        client.webhooks.list({"cursor": "cur_abc", "limit": 50})


class TestGet:
    def test_sends_get_webhooks_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/webhooks/whk_123"
            return json_response(mock_webhook)

        client = make_client(handler)
        webhook = client.webhooks.get("whk_123")
        assert webhook["id"] == "whk_123"
        assert webhook["url"] == "https://example.com/webhooks"
        assert webhook["events"] == ["message.received", "message.sent"]
        assert webhook["active"] is True


class TestUpdate:
    def test_sends_patch_webhooks_id_with_body(self) -> None:
        updated = {**mock_webhook, "url": "https://example.com/new-hook", "active": False}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/webhooks/whk_123"
            body = json.loads(request.content)
            assert body == {
                "url": "https://example.com/new-hook",
                "active": False,
            }
            return json_response(updated)

        client = make_client(handler)
        webhook = client.webhooks.update("whk_123", {
            "url": "https://example.com/new-hook",
            "active": False,
        })
        assert webhook["url"] == "https://example.com/new-hook"
        assert webhook["active"] is False

    def test_updates_events_list(self) -> None:
        updated = {**mock_webhook, "events": ["message.bounced"]}

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"events": ["message.bounced"]}
            return json_response(updated)

        client = make_client(handler)
        webhook = client.webhooks.update("whk_123", {"events": ["message.bounced"]})
        assert webhook["events"] == ["message.bounced"]

    def test_updates_description_to_none(self) -> None:
        updated = {**mock_webhook, "description": None}

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"description": None}
            return json_response(updated)

        client = make_client(handler)
        webhook = client.webhooks.update("whk_123", {"description": None})
        assert webhook["description"] is None

    def test_replaces_authorization(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"authorization": "Bearer key_456"}
            return json_response({**mock_webhook, "has_authorization": True})

        client = make_client(handler)
        webhook = client.webhooks.update("whk_123", {"authorization": "Bearer key_456"})
        assert webhook["has_authorization"] is True

    def test_clears_authorization_with_none(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"authorization": None}
            return json_response(mock_webhook)

        client = make_client(handler)
        webhook = client.webhooks.update("whk_123", {"authorization": None})
        assert webhook["has_authorization"] is False

    def test_sets_and_clears_standard_webhooks_secret(self) -> None:
        bodies: list[object] = []

        def handler(request: httpx.Request) -> httpx.Response:
            bodies.append(json.loads(request.content))
            return json_response({**mock_webhook, "has_standard_webhooks_secret": len(bodies) == 1})

        client = make_client(handler)
        webhook = client.webhooks.update("whk_123", {"standard_webhooks_secret": "whsec_abc"})
        assert webhook["has_standard_webhooks_secret"] is True
        assert "standard_webhooks_secret" not in webhook
        cleared = client.webhooks.update("whk_123", {"standard_webhooks_secret": None})
        assert cleared["has_standard_webhooks_secret"] is False
        assert bodies == [{"standard_webhooks_secret": "whsec_abc"}, {"standard_webhooks_secret": None}]

    def test_sets_and_clears_allowed_senders(self) -> None:
        bodies: list[object] = []

        def handler(request: httpx.Request) -> httpx.Response:
            bodies.append(json.loads(request.content))
            senders = ["jane@customer.com", "customer.org"] if len(bodies) == 1 else None
            return json_response({**mock_webhook, "allowed_senders": senders})

        client = make_client(handler)
        webhook = client.webhooks.update("whk_123", {"allowed_senders": ["jane@customer.com", "customer.org"]})
        assert webhook["allowed_senders"] == ["jane@customer.com", "customer.org"]
        cleared = client.webhooks.update("whk_123", {"allowed_senders": None})
        assert cleared["allowed_senders"] is None
        assert bodies == [{"allowed_senders": ["jane@customer.com", "customer.org"]}, {"allowed_senders": None}]

    def test_omits_authorization_when_absent(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"active": False}
            return json_response({**mock_webhook, "active": False})

        client = make_client(handler)
        client.webhooks.update("whk_123", {"active": False})


class TestDelete:
    def test_sends_delete_webhooks_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/webhooks/whk_123"
            return httpx.Response(204)

        client = make_client(handler)
        result = client.webhooks.delete("whk_123")
        assert result is None


class TestRotateSecret:
    def test_sends_post_rotate_secret(self) -> None:
        response = {
            "secret": "whsec_new_secret",
            "previous_secret_expires_at": "2025-01-08T00:00:00Z",
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/webhooks/whk_123/rotate-secret"
            return json_response(response)

        client = make_client(handler)
        result = client.webhooks.rotate_secret("whk_123")
        assert result["secret"] == "whsec_new_secret"
        assert result["previous_secret_expires_at"] == "2025-01-08T00:00:00Z"


class TestTestWebhook:
    def test_sends_post_test(self) -> None:
        response = {"event_id": "evt_test_123"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/webhooks/whk_123/test"
            return json_response(response)

        client = make_client(handler)
        result = client.webhooks.test("whk_123")
        assert result["event_id"] == "evt_test_123"


class TestListDeliveries:
    def test_sends_get_deliveries(self) -> None:
        response = {
            "data": [mock_delivery],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/webhooks/whk_123/deliveries"
            return json_response(response)

        client = make_client(handler)
        result = client.webhooks.list_deliveries("whk_123")
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == "dlv_001"
        assert result["data"][0]["status"] == "delivered"
        assert result["data"][0]["last_status_code"] == 200

    def test_sends_status_and_event_type_filters(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url.params.get("status")) == "failed"
            assert str(request.url.params.get("event_type")) == "message.bounced"
            return json_response(response)

        client = make_client(handler)
        client.webhooks.list_deliveries("whk_123", {
            "status": "failed",
            "event_type": "message.bounced",
        })

    def test_sends_cursor_and_limit(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url.params.get("cursor")) == "cur_dlv"
            assert str(request.url.params.get("limit")) == "100"
            return json_response(response)

        client = make_client(handler)
        client.webhooks.list_deliveries("whk_123", {
            "cursor": "cur_dlv",
            "limit": 100,
        })

    def test_omits_undefined_params(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert "status" not in request.url.params
            assert "event_type" not in request.url.params
            assert "cursor" not in request.url.params
            assert "limit" not in request.url.params
            return json_response(response)

        client = make_client(handler)
        client.webhooks.list_deliveries("whk_123")
