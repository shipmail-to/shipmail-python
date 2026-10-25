from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_domain = {
    "object": "domain",
    "id": "dom_123",
    "name": "example.com",
    "status": "verified",
    "managed_by": "external",
    "dns_provider": None,
    "mx_verified": True,
    "spf_verified": True,
    "dkim_verified": True,
    "dmarc_verified": True,
    "dmarc_managed_externally": False,
    "outbound_verified": True,
    "catch_all_mailbox_id": None,
    "verified_at": "2025-01-01T00:00:00Z",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z",
}


class TestCreate:
    def test_sends_post_domains_with_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/domains"
            body = json.loads(request.content)
            assert body == {"name": "example.com"}
            return json_response(mock_domain)

        client = make_client(handler)
        domain = client.domains.create({"name": "example.com"})
        assert domain["id"] == "dom_123"
        assert domain["name"] == "example.com"


class TestList:
    def test_sends_get_domains(self) -> None:
        response = {
            "data": [mock_domain],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/domains"
            return json_response(response)

        client = make_client(handler)
        result = client.domains.list()
        assert len(result["data"]) == 1
        assert result["data"][0]["id"] == "dom_123"
        assert result["pagination"]["has_more"] is False

    def test_sends_cursor_and_limit_query_params(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert str(request.url.params.get("cursor")) == "cur_abc"
            assert str(request.url.params.get("limit")) == "25"
            return json_response(response)

        client = make_client(handler)
        client.domains.list({"cursor": "cur_abc", "limit": 25})

    def test_omits_undefined_params(self) -> None:
        response = {
            "data": [],
            "pagination": {"next_cursor": None, "has_more": False},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert "cursor" not in request.url.params
            assert "limit" not in request.url.params
            return json_response(response)

        client = make_client(handler)
        client.domains.list()


class TestGet:
    def test_sends_get_domains_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/domains/dom_123"
            return json_response(mock_domain)

        client = make_client(handler)
        domain = client.domains.get("dom_123")
        assert domain["id"] == "dom_123"
        assert domain["name"] == "example.com"


class TestGetDnsRecords:
    def test_sends_get_domains_id_dns_records(self) -> None:
        response = {
            "object": "dns_record_set",
            "domain_id": "dom_123",
            "domain_name": "example.com",
            "all_verified": True,
            "checked_at": "2026-07-13T12:00:00.000Z",
            "records": [],
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/domains/dom_123/dns-records"
            return json_response(response)

        client = make_client(handler)
        result = client.domains.get_dns_records("dom_123")
        assert result["object"] == "dns_record_set"
        assert result["all_verified"] is True

    @pytest.mark.asyncio
    async def test_async_sends_get_domains_id_dns_records(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/domains/dom_123/dns-records"
            return json_response({
                "object": "dns_record_set",
                "domain_id": "dom_123",
                "domain_name": "example.com",
                "all_verified": False,
                "checked_at": "2026-07-13T12:00:00.000Z",
                "records": [],
            })

        client = make_async_client(handler)
        result = await client.domains.get_dns_records("dom_123")
        assert result["object"] == "dns_record_set"


mock_health = {
    "object": "domain_health",
    "domain_id": "dom_123",
    "domain": "example.com",
    "generated_at": "2026-10-18T12:00:00.000Z",
    "dns": {"mx": True, "spf": True, "dkim": True, "dmarc": False, "last_checked_at": None},
    "blocklist": {"list": "spamhaus_dbl", "listed": False, "listed_since": None},
    "delivery": {
        "since": "2026-09-18T12:00:00.000Z",
        "until": "2026-10-18T12:00:00.000Z",
        "recipients": 2,
        "delivered": 2,
        "bounced": 0,
        "deferred": 0,
        "complained": 0,
        "failed": 0,
        "suppressed": 0,
        "queued": 0,
        "sent": 0,
        "delivery_rate": 100,
        "providers": [
            {
                "provider": "google",
                "recipients": 2,
                "delivered": 2,
                "bounced": 0,
                "deferred": 0,
                "complained": 0,
                "delivery_rate": 100,
            },
        ],
    },
}


class TestGetHealth:
    def test_sends_get_domains_id_health(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/domains/dom_123/health"
            return json_response(mock_health)

        client = make_client(handler)
        result = client.domains.get_health("dom_123")
        assert result["object"] == "domain_health"
        assert result["delivery"]["providers"][0]["provider"] == "google"

    @pytest.mark.asyncio
    async def test_async_sends_get_domains_id_health(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/domains/dom_123/health"
            return json_response(mock_health)

        client = make_async_client(handler)
        result = await client.domains.get_health("dom_123")
        assert result["blocklist"]["list"] == "spamhaus_dbl"


class TestUpdate:
    def test_sends_patch_domains_id_with_body(self) -> None:
        updated = {**mock_domain, "catch_all_mailbox_id": "mbx_456"}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/domains/dom_123"
            body = json.loads(request.content)
            assert body == {"catch_all_mailbox_id": "mbx_456"}
            return json_response(updated)

        client = make_client(handler)
        domain = client.domains.update("dom_123", {"catch_all_mailbox_id": "mbx_456"})
        assert domain["catch_all_mailbox_id"] == "mbx_456"

    def test_sends_null_to_clear_catch_all_mailbox_id(self) -> None:
        updated = {**mock_domain, "catch_all_mailbox_id": None}

        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body == {"catch_all_mailbox_id": None}
            return json_response(updated)

        client = make_client(handler)
        domain = client.domains.update("dom_123", {"catch_all_mailbox_id": None})
        assert domain["catch_all_mailbox_id"] is None


class TestDelete:
    def test_sends_delete_domains_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/domains/dom_123"
            return httpx.Response(204)

        client = make_client(handler)
        result = client.domains.delete("dom_123")
        assert result is None


class TestVerify:
    def test_sends_post_domains_id_verification(self) -> None:
        verification_result = {
            "all_verified": True,
            "records": {
                "mx": True,
                "spf": True,
                "dkim": True,
                "dmarc": True,
            },
            "outbound_verified": True,
            "outbound_error": False,
            "existing_spf": "v=spf1 include:_spf.google.com ~all",
            "suggested_spf": "v=spf1 include:_spf.google.com include:amazonses.com ~all",
            "conflicting_mx": [],
            "dmarc_valid": True,
            "dmarc_exact_match": True,
            "dmarc_record_value": "v=DMARC1; p=reject",
            "dmarc_managed_externally": False,
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/domains/dom_123/verification"
            return json_response(verification_result)

        client = make_client(handler)
        result = client.domains.verify("dom_123")
        assert result["all_verified"] is True
        assert result["records"]["mx"] is True
        assert result["records"]["spf"] is True
        assert result["records"]["dkim"] is True
        assert result["records"]["dmarc"] is True
        assert result["outbound_verified"] is True
        assert result["outbound_error"] is False
        assert result["conflicting_mx"] == []
