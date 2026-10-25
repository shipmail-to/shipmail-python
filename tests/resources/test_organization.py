from __future__ import annotations

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

ACCESS = {
    "object": "organization_access",
    "organization": {"id": "org_1", "name": "Acme"},
    "plan": "team",
    "has_access": True,
    "trial": {"active": True, "ends_at": "2026-10-19T00:00:00.000Z", "eligible": False},
    "mailboxes": {"limit": 3, "used": 1},
    "newsletters_allowed": False,
}


def handler(request: httpx.Request) -> httpx.Response:
    assert request.method == "GET"
    assert request.url.path == "/v1/organization/access"
    return json_response(ACCESS)


class TestAccess:
    def test_returns_access(self) -> None:
        assert make_client(handler).organization.access() == ACCESS

    @pytest.mark.asyncio
    async def test_returns_access_async(self) -> None:
        assert await make_async_client(handler).organization.access() == ACCESS
