from __future__ import annotations

import json
from collections.abc import Callable

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

ACCESS = {
    "object": "organization_access",
    "organization": {"id": "org_1", "name": "Acme", "default_timezone": "Europe/Lisbon"},
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


ORGANIZATION = {
    "object": "organization",
    "id": "org_1",
    "name": "Acme",
    "default_timezone": "Europe/Paris",
}

AI_SETTINGS = {
    "object": "organization_ai_settings",
    "models_enabled": True,
    "automatic_send_enabled": True,
    "effective": {"models_enabled": True, "automatic_send_enabled": False},
}


def expect(
    method: str, path: str, response: object, body: object | None = None
) -> Callable[[httpx.Request], httpx.Response]:
    def handle(request: httpx.Request) -> httpx.Response:
        assert request.method == method
        assert request.url.path == path
        if body is not None:
            assert json.loads(request.content) == body
        return json_response(response)

    return handle


class TestSettings:
    def test_get(self) -> None:
        client = make_client(expect("GET", "/v1/organization", ORGANIZATION))
        assert client.organization.get() == ORGANIZATION

    def test_update_clears_zone(self) -> None:
        cleared = {**ORGANIZATION, "default_timezone": None}
        client = make_client(expect("PATCH", "/v1/organization", cleared, {"default_timezone": None}))
        assert client.organization.update({"default_timezone": None}) == cleared

    def test_get_ai_settings(self) -> None:
        client = make_client(expect("GET", "/v1/organization/ai-settings", AI_SETTINGS))
        assert client.organization.get_ai_settings() == AI_SETTINGS

    def test_update_ai_settings(self) -> None:
        client = make_client(
            expect("PATCH", "/v1/organization/ai-settings", AI_SETTINGS, {"models_enabled": True})
        )
        assert client.organization.update_ai_settings({"models_enabled": True}) == AI_SETTINGS

    @pytest.mark.asyncio
    async def test_update_async(self) -> None:
        client = make_async_client(
            expect("PATCH", "/v1/organization", ORGANIZATION, {"default_timezone": "Europe/Paris"})
        )
        assert await client.organization.update({"default_timezone": "Europe/Paris"}) == ORGANIZATION

    @pytest.mark.asyncio
    async def test_get_ai_settings_async(self) -> None:
        client = make_async_client(expect("GET", "/v1/organization/ai-settings", AI_SETTINGS))
        assert await client.organization.get_ai_settings() == AI_SETTINGS
