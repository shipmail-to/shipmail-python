from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

DOMAIN_ID = "txdom_0123456789abcdefghjkmnpq"
SENDER_ID = "txbind_0123456789abcdefghjkmnpq"
MAILBOX_ID = "550e8400-e29b-41d4-a716-446655440000"

mock_domain = {
    "object": "transactional_domain",
    "id": DOMAIN_ID,
    "name": "mail.example.com",
    "root_domain": "example.com",
    "status": "pending",
    "mail_from_domain": "mail.mail.example.com",
    "dns_records": [
        {
            "key": "dkim",
            "type": "TXT",
            "host": "shipmail._domainkey.mail.example.com",
            "value": "v=DKIM1; k=rsa; p=abc",
            "priority": None,
            "ttl": 300,
            "description": "Signs your transactional email so inboxes trust it.",
            "status": "pending",
        }
    ],
    "verified_at": None,
    "created_at": "2026-11-08T09:00:00.000Z",
}

mock_sender = {
    "object": "transactional_sender",
    "id": SENDER_ID,
    "from": "hello@mail.example.com",
    "display_name": "Acme",
    "domain_id": DOMAIN_ID,
    "mailbox_id": MAILBOX_ID,
    "reply_to": "support@example.com",
    "state": "active",
    "refuse_disposable": False,
    "smtp_enabled": False,
    "created_at": "2026-11-08T09:00:00.000Z",
}


class TestTransactionalDomains:
    def test_lists_creates_gets_verifies_and_deletes(self) -> None:
        seen: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(f"{request.method} {request.url.path}")
            if request.method == "DELETE":
                return httpx.Response(204)
            if request.method == "GET" and request.url.path == "/v1/transactional-domains":
                return json_response({"object": "list", "data": [mock_domain]})
            if request.url.path.endswith("/verify"):
                return json_response({**mock_domain, "status": "verified"})
            if request.method == "POST":
                assert json.loads(request.content) == {"root_domain": "example.com", "subdomain": "mail"}
                return json_response(mock_domain, 201)
            return json_response(mock_domain)

        domains = make_client(handler).transactional_domains
        assert domains.list()["data"][0]["id"] == DOMAIN_ID
        assert domains.create({"root_domain": "example.com", "subdomain": "mail"})["dns_records"][0]["key"] == "dkim"
        assert domains.get(DOMAIN_ID)["name"] == "mail.example.com"
        assert domains.verify(DOMAIN_ID)["status"] == "verified"
        domains.delete(DOMAIN_ID)
        assert seen == [
            "GET /v1/transactional-domains",
            "POST /v1/transactional-domains",
            f"GET /v1/transactional-domains/{DOMAIN_ID}",
            f"POST /v1/transactional-domains/{DOMAIN_ID}/verify",
            f"DELETE /v1/transactional-domains/{DOMAIN_ID}",
        ]

    @pytest.mark.asyncio
    async def test_async_verifies(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == f"/v1/transactional-domains/{DOMAIN_ID}/verify"
            return json_response({**mock_domain, "status": "verified"})

        result = await make_async_client(handler).transactional_domains.verify(DOMAIN_ID)
        assert result["status"] == "verified"


class TestTransactionalSenders:
    def test_lists_filtered_by_domain(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/transactional-senders"
            assert "domain_id" not in request.url.params
            return json_response({"object": "list", "data": [mock_sender]})

        client = make_client(handler)
        client.transactional_senders.list()

        def filtered(request: httpx.Request) -> httpx.Response:
            assert request.url.params["domain_id"] == DOMAIN_ID
            return json_response({"object": "list", "data": [mock_sender]})

        result = make_client(filtered).transactional_senders.list({"domain_id": DOMAIN_ID})
        assert result["data"][0]["from"] == "hello@mail.example.com"

    def test_creates_gets_and_updates(self) -> None:
        seen: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            seen.append(f"{request.method} {request.url.path}")
            if request.method == "POST":
                assert json.loads(request.content) == {
                    "domain_id": DOMAIN_ID,
                    "mailbox_id": MAILBOX_ID,
                    "local_part": "hello",
                    "display_name": "Acme",
                }
                return json_response(mock_sender, 201)
            if request.method == "PATCH":
                assert json.loads(request.content) == {"state": "disabled"}
                return json_response({**mock_sender, "state": "disabled"})
            return json_response(mock_sender)

        senders = make_client(handler).transactional_senders
        senders.create(
            {"domain_id": DOMAIN_ID, "mailbox_id": MAILBOX_ID, "local_part": "hello", "display_name": "Acme"}
        )
        senders.get(SENDER_ID)
        assert senders.update(SENDER_ID, {"state": "disabled"})["state"] == "disabled"
        assert seen == [
            "POST /v1/transactional-senders",
            f"GET /v1/transactional-senders/{SENDER_ID}",
            f"PATCH /v1/transactional-senders/{SENDER_ID}",
        ]

    @pytest.mark.asyncio
    async def test_async_updates(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert json.loads(request.content) == {"mailbox_id": MAILBOX_ID, "refuse_disposable": True}
            return json_response({**mock_sender, "refuse_disposable": True})

        client = make_async_client(handler)
        result = await client.transactional_senders.update(
            SENDER_ID, {"mailbox_id": MAILBOX_ID, "refuse_disposable": True}
        )
        assert result["refuse_disposable"] is True
