from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_customer = {
    "object": "customer",
    "id": "cust_123",
    "name": "Jane Doe",
    "company": "Acme",
    "notes": None,
    "service_level_id": "svl_123",
    "fields": {"plan": "enterprise"},
    "tags": ["vip"],
    "identifiers": [{"kind": "email", "value": "jane@acme.com"}],
    "external_ids": [{"source": "hubspot", "external_id": "contact/42", "url": None}],
    "created_at": "2026-11-01T00:00:00Z",
    "updated_at": "2026-11-01T00:00:00Z",
}


class TestList:
    def test_sends_the_filters(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/customers"
            assert dict(request.url.params) == {"domain": "acme.com", "limit": "10"}
            return json_response({"data": [mock_customer], "pagination": {"next_cursor": None, "has_more": False, "limit": 10}})

        result = make_client(handler).customers.list({"domain": "acme.com", "limit": 10})
        assert result["data"][0]["id"] == "cust_123"

    def test_sends_the_tag_filter(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert dict(request.url.params) == {"tag": "vip"}
            return json_response({"data": [mock_customer], "pagination": {"next_cursor": None, "has_more": False, "limit": 20}})

        result = make_client(handler).customers.list({"tag": "vip"})
        assert result["data"][0]["tags"] == ["vip"]

    @pytest.mark.asyncio
    async def test_async_sends_the_tag_filter(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert dict(request.url.params) == {"tag": "vip"}
            return json_response({"data": [mock_customer], "pagination": {"next_cursor": None, "has_more": False, "limit": 20}})

        result = await make_async_client(handler).customers.list({"tag": "vip"})
        assert result["data"][0]["tags"] == ["vip"]


class TestCrud:
    def test_uses_the_customer_paths(self) -> None:
        calls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(f"{request.method} {request.url.path}")
            if request.method == "DELETE":
                return httpx.Response(204)
            return json_response(mock_customer, 201 if request.method == "POST" else 200)

        client = make_client(handler)
        client.customers.create({"name": "Jane Doe"})
        client.customers.get("cust_123")
        client.customers.update("cust_123", {"notes": "VIP"})
        client.customers.remove("cust_123")
        assert calls == [
            "POST /v1/customers",
            "GET /v1/customers/cust_123",
            "PATCH /v1/customers/cust_123",
            "DELETE /v1/customers/cust_123",
        ]


class TestUpsertByExternalId:
    def test_encodes_the_external_id_once(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PUT"
            assert request.url.raw_path == b"/v1/customers/external/hubspot/contact%2F42"
            assert json.loads(request.content) == {"name": "Jane Doe", "tags": ["vip", "beta"]}
            return json_response(mock_customer)

        result = make_client(handler).customers.upsert_by_external_id(
            "hubspot", "contact/42", {"name": "Jane Doe", "tags": ["vip", "beta"]}
        )
        assert result["id"] == "cust_123"

    @pytest.mark.asyncio
    async def test_async_upsert(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PUT"
            assert request.url.raw_path == b"/v1/customers/external/stripe/cus_1"
            return json_response(mock_customer, 201)

        client = make_async_client(handler)
        result = await client.customers.upsert_by_external_id("stripe", "cus_1", {})
        assert result["object"] == "customer"


class TestReferenceLists:
    def test_lists_service_levels_and_fields(self) -> None:
        paths: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            paths.append(request.url.path)
            return json_response({"data": []})

        client = make_client(handler)
        client.customers.list_service_levels()
        client.customers.list_fields()
        assert paths == ["/v1/service-levels", "/v1/customer-fields"]

    @pytest.mark.asyncio
    async def test_async_lists(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response({"data": []})

        client = make_async_client(handler)
        assert (await client.customers.list_service_levels()) == {"data": []}
        assert (await client.customers.list_fields()) == {"data": []}
