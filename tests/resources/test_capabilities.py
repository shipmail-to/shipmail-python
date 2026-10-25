from __future__ import annotations

import httpx

from tests.conftest import json_response, make_client


class TestGet:
    def test_returns_effective_capabilities(self) -> None:
        response = {
            "capability_version": "1.1.0",
            "scopes": ["messages:read", "messages:send"],
            "constraints": {
                "mailbox_ids": ["mbx_123"],
                "domain_ids": None,
                "audience_ids": None,
                "resource_semantics": "legacy-intersection",
            },
            "allowed_mcp_tools": ["shipmail_list_messages", "shipmail_send_message"],
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/capabilities"
            return json_response(response)

        result = make_client(handler).capabilities.get()
        assert result["allowed_mcp_tools"] == [
            "shipmail_list_messages",
            "shipmail_send_message",
        ]
