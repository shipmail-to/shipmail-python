from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from shipmail import NotFoundError, Shipmail, ShipmailError, __version__
from shipmail._base_client import RequestOptions
from shipmail._errors import InternalServerError

from .conftest import json_response, make_client

STATUS_OK = {"status": "ok", "version": "1", "time": "t", "request_id": "r"}


class TestDefaultHeaders:
    def test_sends_authorization_bearer_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["authorization"] == "Bearer sm_live_test_key"
            return json_response(STATUS_OK)

        client = make_client(handler)
        result = client.status.get()
        assert result["status"] == "ok"

    def test_sends_user_agent_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["user-agent"] == f"shipmail-python/{__version__}"
            return json_response(STATUS_OK)

        client = make_client(handler)
        client.status.get()

    def test_sends_accept_json_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["accept"] == "application/json"
            return json_response(STATUS_OK)

        client = make_client(handler)
        client.status.get()

    def test_sends_content_type_json_for_post(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["content-type"] == "application/json"
            return json_response({"id": "dom_123", "name": "example.com"})

        client = make_client(handler)
        client.domains.create({"name": "example.com"})

    def test_no_content_type_for_get(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "content-type" not in request.headers
            return json_response(STATUS_OK)

        client = make_client(handler)
        client.status.get()


class TestRetryBehavior:
    def test_retries_on_5xx_up_to_max_retries(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] < 3:
                return json_response(
                    {"error": {"type": "internal_error", "message": "Server error"}},
                    500,
                )
            return json_response(STATUS_OK)

        client = make_client(handler, max_retries=2)
        result = client.status.get()
        assert result["status"] == "ok"
        assert attempts["count"] == 3

    def test_retries_on_429_responses(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] < 2:
                return json_response(
                    {"error": {"type": "rate_limit_error", "message": "Too many requests"}},
                    429,
                )
            return json_response(STATUS_OK)

        client = make_client(handler, max_retries=2)
        result = client.status.get()
        assert result["status"] == "ok"
        assert attempts["count"] == 2

    def test_no_retry_on_4xx_non_429(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            return json_response(
                {"error": {"type": "not_found", "message": "Not found"}},
                404,
            )

        client = make_client(handler, max_retries=2)
        with pytest.raises(NotFoundError):
            client.status.get()
        assert attempts["count"] == 1

    def test_throws_after_exhausting_retries_on_5xx(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            return json_response(
                {"error": {"type": "internal_error", "message": "Server error"}},
                500,
            )

        client = make_client(handler, max_retries=2)
        with pytest.raises(InternalServerError):
            client.status.get()
        assert attempts["count"] == 3

    def test_retries_on_network_errors(self) -> None:
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise httpx.ConnectError("Connection refused")
            return json_response(STATUS_OK)

        client = make_client(handler, max_retries=2)
        result = client.status.get()
        assert result["status"] == "ok"
        assert attempts["count"] == 3


class TestQueryParams:
    def test_appends_query_params_to_url(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            qs = parse_qs(parsed.query)
            assert qs["cursor"] == ["abc123"]
            assert qs["limit"] == ["10"]
            return json_response({"data": [], "pagination": {"next_cursor": None, "has_more": False}})

        client = make_client(handler)
        client.domains.list({"cursor": "abc123", "limit": 10})

    def test_omits_none_query_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            assert parsed.query == ""
            return json_response({"data": [], "pagination": {"next_cursor": None, "has_more": False}})

        client = make_client(handler)
        client.domains.list()

    def test_boolean_query_params_serialized(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            qs = parse_qs(parsed.query)
            assert qs["active"] == ["true"]
            return json_response({"ok": True})

        client = make_client(handler)
        client.request(RequestOptions(method="GET", path="/test", query={"active": True}))


class TestResponseHandling:
    def test_204_returns_none(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(204)

        client = make_client(handler)
        result = client.domains.delete("dom_123")
        assert result is None


class TestErrorMapping:
    def test_maps_api_error_body_to_typed_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(
                {"error": {"type": "not_found", "message": "Domain not found", "request_id": "req_abc"}},
                404,
            )

        client = make_client(handler)
        with pytest.raises(NotFoundError) as exc_info:
            client.domains.get("dom_missing")

        err = exc_info.value
        assert str(err) == "Domain not found"
        assert err.status == 404
        assert err.type == "not_found"
        assert err.request_id == "req_abc"
        assert err.retryable is False

    def test_falls_back_to_generic_error_for_non_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="Internal Server Error", headers={"x-request-id": "req_hdr"})

        client = make_client(handler)
        with pytest.raises(ShipmailError) as exc_info:
            client.status.get()

        err = exc_info.value
        assert err.status == 500
        assert err.retryable is True
        assert err.request_id == "req_hdr"

    def test_falls_back_to_generic_error_for_malformed_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response({"message": "Bad"}, 400)

        client = make_client(handler)
        with pytest.raises(ShipmailError) as exc_info:
            client.status.get()

        err = exc_info.value
        assert str(err) == "Request failed with status 400"
        assert err.retryable is False


class TestConstructor:
    def test_string_api_key_creates_valid_client(self) -> None:
        client = Shipmail("sm_live_my_key")
        assert client.domains is not None
        assert client.mailboxes is not None
        assert client.messages is not None
        assert client.capabilities is not None
        assert client.threads is not None
        assert client.webhooks is not None
        assert client.status is not None
        assert client.suppressions is not None


class TestWebhookDeliveryReplay:
    def test_gets_delivery_detail(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/webhooks/whk_123/deliveries/dlv_123"
            return json_response({"id": "dlv_123", "payload": {"event_id": "evt_123"}})

        result = make_client(handler).webhooks.get_delivery("whk_123", "dlv_123")
        assert result["payload"] == {"event_id": "evt_123"}

    def test_replays_delivery_with_idempotency_key(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/webhooks/whk_123/deliveries/dlv_123/replay"
            assert request.headers["idempotency-key"] == "idem_replay_123"
            return json_response({"id": "dlv_replay", "replayed_from_delivery_id": "dlv_123"}, 201)

        result = make_client(handler).webhooks.replay_delivery(
            "whk_123",
            "dlv_123",
            {"idempotency_key": "idem_replay_123"},
        )
        assert result["replayed_from_delivery_id"] == "dlv_123"


class TestRequestBody:
    def test_sends_json_body_for_post(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"name": "example.com"}
            return json_response({"id": "dom_123", "name": "example.com"})

        client = make_client(handler)
        client.domains.create({"name": "example.com"})


class TestContextManager:
    def test_with_statement(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(STATUS_OK)

        with make_client(handler) as client:
            result = client.status.get()
            assert result["status"] == "ok"


class TestRepr:
    def test_repr_redacts_api_key(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response(STATUS_OK)

        client = make_client(handler)
        r = repr(client)
        assert "sm_live_test_key" not in r
        assert "sm_live_..." in r
        assert "Shipmail(" in r
