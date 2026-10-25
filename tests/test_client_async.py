from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from shipmail import AsyncShipmail, NotFoundError, ShipmailError, __version__
from shipmail._base_client import RequestOptions
from shipmail._errors import InternalServerError

from .conftest import json_response, make_async_client

STATUS_OK = {"status": "ok", "version": "1", "time": "t", "request_id": "r"}


class TestDefaultHeaders:
    @pytest.mark.asyncio
    async def test_sends_authorization_bearer_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["authorization"] == "Bearer sm_live_test_key"
            return json_response(STATUS_OK)

        client = make_async_client(handler)
        result = await client.status.get()
        assert result["status"] == "ok"

    @pytest.mark.asyncio
    async def test_sends_user_agent_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["user-agent"] == f"shipmail-python/{__version__}"
            return json_response(STATUS_OK)

        client = make_async_client(handler)
        await client.status.get()

    @pytest.mark.asyncio
    async def test_sends_accept_json_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["accept"] == "application/json"
            return json_response(STATUS_OK)

        client = make_async_client(handler)
        await client.status.get()

    @pytest.mark.asyncio
    async def test_sends_content_type_json_for_post(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["content-type"] == "application/json"
            return json_response({"id": "dom_123", "name": "example.com"})

        client = make_async_client(handler)
        await client.domains.create({"name": "example.com"})

    @pytest.mark.asyncio
    async def test_no_content_type_for_get(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "content-type" not in request.headers
            return json_response(STATUS_OK)

        client = make_async_client(handler)
        await client.status.get()


class TestRetryBehavior:
    @pytest.mark.asyncio
    async def test_retries_on_5xx_up_to_max_retries(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] < 3:
                return json_response(
                    {"error": {"type": "internal_error", "message": "Server error"}},
                    500,
                )
            return json_response(STATUS_OK)

        client = make_async_client(handler, max_retries=2)
        result = await client.status.get()
        assert result["status"] == "ok"
        assert attempts["count"] == 3

    @pytest.mark.asyncio
    async def test_retries_on_429_responses(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] < 2:
                return json_response(
                    {"error": {"type": "rate_limit_error", "message": "Too many requests"}},
                    429,
                )
            return json_response(STATUS_OK)

        client = make_async_client(handler, max_retries=2)
        result = await client.status.get()
        assert result["status"] == "ok"
        assert attempts["count"] == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_4xx_non_429(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            return json_response(
                {"error": {"type": "not_found", "message": "Not found"}},
                404,
            )

        client = make_async_client(handler, max_retries=2)
        with pytest.raises(NotFoundError):
            await client.status.get()
        assert attempts["count"] == 1

    @pytest.mark.asyncio
    async def test_throws_after_exhausting_retries_on_5xx(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            return json_response(
                {"error": {"type": "internal_error", "message": "Server error"}},
                500,
            )

        client = make_async_client(handler, max_retries=2)
        with pytest.raises(InternalServerError):
            await client.status.get()
        assert attempts["count"] == 3

    @pytest.mark.asyncio
    async def test_retries_on_network_errors(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise httpx.ConnectError("Connection refused")
            return json_response(STATUS_OK)

        client = make_async_client(handler, max_retries=2)
        result = await client.status.get()
        assert result["status"] == "ok"
        assert attempts["count"] == 3


class TestQueryParams:
    @pytest.mark.asyncio
    async def test_appends_query_params_to_url(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            qs = parse_qs(parsed.query)
            assert qs["cursor"] == ["abc123"]
            assert qs["limit"] == ["10"]
            return json_response({"data": [], "pagination": {"next_cursor": None, "has_more": False}})

        client = make_async_client(handler)
        await client.domains.list({"cursor": "abc123", "limit": 10})

    @pytest.mark.asyncio
    async def test_omits_none_query_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            assert parsed.query == ""
            return json_response({"data": [], "pagination": {"next_cursor": None, "has_more": False}})

        client = make_async_client(handler)
        await client.domains.list()

    @pytest.mark.asyncio
    async def test_boolean_query_params_serialized(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            qs = parse_qs(parsed.query)
            assert qs["active"] == ["true"]
            return json_response({"ok": True})

        client = make_async_client(handler)
        await client.request(RequestOptions(method="GET", path="/test", query={"active": True}))


class TestResponseHandling:
    @pytest.mark.asyncio
    async def test_204_returns_none(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(204)

        client = make_async_client(handler)
        result = await client.domains.delete("dom_123")
        assert result is None


class TestErrorMapping:
    @pytest.mark.asyncio
    async def test_maps_api_error_body_to_typed_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(
                {"error": {"type": "not_found", "message": "Domain not found", "request_id": "req_abc"}},
                404,
            )

        client = make_async_client(handler)
        with pytest.raises(NotFoundError) as exc_info:
            await client.domains.get("dom_missing")

        err = exc_info.value
        assert str(err) == "Domain not found"
        assert err.status == 404
        assert err.type == "not_found"
        assert err.request_id == "req_abc"
        assert err.retryable is False

    @pytest.mark.asyncio
    async def test_falls_back_to_generic_error_for_non_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="Internal Server Error", headers={"x-request-id": "req_hdr"})

        client = make_async_client(handler)
        with pytest.raises(ShipmailError) as exc_info:
            await client.status.get()

        err = exc_info.value
        assert err.status == 500
        assert err.retryable is True
        assert err.request_id == "req_hdr"

    @pytest.mark.asyncio
    async def test_falls_back_to_generic_error_for_malformed_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response({"message": "Bad"}, 400)

        client = make_async_client(handler)
        with pytest.raises(ShipmailError) as exc_info:
            await client.status.get()

        err = exc_info.value
        assert str(err) == "Request failed with status 400"
        assert err.retryable is False


class TestConstructor:
    def test_string_api_key_creates_valid_client(self) -> None:
        client = AsyncShipmail("sm_live_my_key")
        assert client.domains is not None
        assert client.mailboxes is not None
        assert client.messages is not None
        assert client.capabilities is not None
        assert client.threads is not None
        assert client.webhooks is not None
        assert client.status is not None
        assert client.suppressions is not None


class TestWebhookDeliveryReplay:
    @pytest.mark.asyncio
    async def test_gets_delivery_detail(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/webhooks/whk_123/deliveries/dlv_123"
            return json_response({"id": "dlv_123", "payload": {"event_id": "evt_123"}})

        result = await make_async_client(handler).webhooks.get_delivery("whk_123", "dlv_123")
        assert result["payload"] == {"event_id": "evt_123"}

    @pytest.mark.asyncio
    async def test_replays_delivery_with_idempotency_key(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/webhooks/whk_123/deliveries/dlv_123/replay"
            assert request.headers["idempotency-key"] == "idem_replay_123"
            return json_response({"id": "dlv_replay", "replayed_from_delivery_id": "dlv_123"}, 201)

        result = await make_async_client(handler).webhooks.replay_delivery(
            "whk_123",
            "dlv_123",
            {"idempotency_key": "idem_replay_123"},
        )
        assert result["replayed_from_delivery_id"] == "dlv_123"


class TestWebhookAuthorization:
    @pytest.mark.asyncio
    async def test_creates_webhook_with_authorization(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert json.loads(request.content)["authorization"] == "Bearer key_123"
            return json_response({"id": "whk_123", "has_authorization": True, "secret": "whsec_abc"}, 201)

        result = await make_async_client(handler).webhooks.create(
            {"url": "https://example.com/hook", "events": ["message.received"], "authorization": "Bearer key_123"}
        )
        assert result["has_authorization"] is True

    @pytest.mark.asyncio
    async def test_clears_authorization_with_none(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert json.loads(request.content) == {"authorization": None}
            return json_response({"id": "whk_123", "has_authorization": False})

        result = await make_async_client(handler).webhooks.update("whk_123", {"authorization": None})
        assert result["has_authorization"] is False


class TestWebhookStandardWebhooksSecret:
    @pytest.mark.asyncio
    async def test_creates_webhook_with_standard_webhooks_secret(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content)["standard_webhooks_secret"] == "whsec_abc"
            return json_response(
                {"id": "whk_123", "has_standard_webhooks_secret": True, "secret": "whsec_own"}, 201
            )

        result = await make_async_client(handler).webhooks.create(
            {"url": "https://example.com/hook", "events": ["message.received"], "standard_webhooks_secret": "whsec_abc"}
        )
        assert result["has_standard_webhooks_secret"] is True

    @pytest.mark.asyncio
    async def test_clears_standard_webhooks_secret_with_none(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {"standard_webhooks_secret": None}
            return json_response({"id": "whk_123", "has_standard_webhooks_secret": False})

        result = await make_async_client(handler).webhooks.update("whk_123", {"standard_webhooks_secret": None})
        assert result["has_standard_webhooks_secret"] is False


class TestRequestBody:
    @pytest.mark.asyncio
    async def test_sends_json_body_for_post(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"name": "example.com"}
            return json_response({"id": "dom_123", "name": "example.com"})

        client = make_async_client(handler)
        await client.domains.create({"name": "example.com"})


class TestAsyncContextManager:
    @pytest.mark.asyncio
    async def test_async_with_statement(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(STATUS_OK)

        async with make_async_client(handler) as client:
            result = await client.status.get()
            assert result["status"] == "ok"


class TestRepr:
    def test_repr_redacts_api_key(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(STATUS_OK)

        client = make_async_client(handler)
        r = repr(client)
        assert "sm_live_test_key" not in r
        assert "sm_live_..." in r
        assert "AsyncShipmail(" in r


class TestWebhookAllowedSenders:
    @pytest.mark.asyncio
    async def test_creates_webhook_with_allowed_senders(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content)["allowed_senders"] == ["customer.org"]
            return json_response({"id": "whk_123", "allowed_senders": ["customer.org"], "secret": "whsec_own"}, 201)

        result = await make_async_client(handler).webhooks.create(
            {"url": "https://example.com/hook", "events": ["message.received"], "allowed_senders": ["customer.org"]}
        )
        assert result["allowed_senders"] == ["customer.org"]

    @pytest.mark.asyncio
    async def test_clears_allowed_senders_with_none(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {"allowed_senders": None}
            return json_response({"id": "whk_123", "allowed_senders": None})

        result = await make_async_client(handler).webhooks.update("whk_123", {"allowed_senders": None})
        assert result["allowed_senders"] is None
