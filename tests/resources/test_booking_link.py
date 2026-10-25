from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_link = {
    "object": "booking_link",
    "id": "bkp_link",
    "mailbox": "orders@papertrail-studio.test",
    "slug": "o--abc123",
    "url": "https://shipmail.to/book/papertrail-studio.test/o--abc123",
    "name": "Call with Sam",
    "description": None,
    "duration_minutes": 30,
    "timezone": "Europe/Lisbon",
    "offered_ranges": [{"start": "2026-11-02T09:00:00.000Z", "end": "2026-11-02T12:00:00.000Z"}],
    "source_page_id": None,
    "buffer_minutes": 0,
    "minimum_notice_minutes": 0,
    "conferencing_provider": None,
    "max_bookings": 1,
    "bookings_count": 0,
    "expires_at": None,
    "status": "open",
    "created_at": "2026-10-21T10:00:00.000Z",
}


class TestCreate:
    def test_sends_post_booking_links(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/booking-links"
            body = json.loads(request.content)
            assert body["offered_ranges"] == mock_link["offered_ranges"]
            assert body["max_bookings"] is None
            return json_response(mock_link, 201)

        client = make_client(handler)
        link = client.booking_links.create(
            {
                "name": "Call with Sam",
                "mailbox": "orders@papertrail-studio.test",
                "duration_minutes": 30,
                "timezone": "Europe/Lisbon",
                "offered_ranges": [
                    {"start": "2026-11-02T09:00:00.000Z", "end": "2026-11-02T12:00:00.000Z"}
                ],
                "max_bookings": None,
            }
        )
        assert link["object"] == "booking_link"


class TestList:
    def test_sends_get_booking_links_with_status(self) -> None:
        response = {"data": [mock_link], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/booking-links"
            assert request.url.params["status"] == "open"
            assert request.url.params["limit"] == "10"
            return json_response(response)

        client = make_client(handler)
        result = client.booking_links.list({"status": "open", "limit": 10})
        assert result["data"][0]["id"] == "bkp_link"


class TestGet:
    def test_sends_get_booking_links_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/booking-links/bkp_link"
            return json_response(mock_link)

        client = make_client(handler)
        assert client.booking_links.get("bkp_link")["id"] == "bkp_link"


class TestUpdate:
    def test_sends_patch_booking_links_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/booking-links/bkp_link"
            assert json.loads(request.content) == {"max_bookings": 3}
            return json_response({**mock_link, "max_bookings": 3})

        client = make_client(handler)
        link = client.booking_links.update("bkp_link", {"max_bookings": 3})
        assert link["max_bookings"] == 3


class TestRevoke:
    def test_sends_post_booking_links_id_revoke(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/booking-links/bkp_link/revoke"
            return json_response({**mock_link, "status": "revoked"})

        client = make_client(handler)
        assert client.booking_links.revoke("bkp_link")["status"] == "revoked"


class TestAsync:
    @pytest.mark.asyncio
    async def test_revoke(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/booking-links/bkp_link/revoke"
            return json_response({**mock_link, "status": "revoked"})

        client = make_async_client(handler)
        link = await client.booking_links.revoke("bkp_link")
        assert link["status"] == "revoked"

    @pytest.mark.asyncio
    async def test_list_sends_status(self) -> None:
        response = {"data": [mock_link], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/booking-links"
            assert request.url.params["status"] == "revoked"
            return json_response(response)

        client = make_async_client(handler)
        result = await client.booking_links.list({"status": "revoked"})
        assert result["data"][0]["id"] == "bkp_link"
