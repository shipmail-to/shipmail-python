from __future__ import annotations

import httpx

from tests.conftest import json_response, make_client

mock_status = {
    "status": "operational",
    "version": "1.0.0",
    "time": "2025-01-01T00:00:00Z",
    "request_id": "req_abc123",
}


class TestGet:
    def test_returns_status_response(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/status"
            return json_response(mock_status)

        client = make_client(handler)
        result = client.status.get()
        assert result["status"] == "operational"
        assert result["version"] == "1.0.0"
        assert result["time"] == "2025-01-01T00:00:00Z"
        assert result["request_id"] == "req_abc123"

    def test_does_not_send_request_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.content == b""
            return json_response(mock_status)

        client = make_client(handler)
        client.status.get()

    def test_includes_authorization_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers.get("authorization") == "Bearer sm_live_test_key"
            return json_response(mock_status)

        client = make_client(handler)
        client.status.get()
