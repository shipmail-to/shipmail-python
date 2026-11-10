from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

mock_page = {
    "object": "booking_page",
    "id": "bkp_1",
    "mailbox": "orders@papertrail-studio.test",
    "slug": "intro",
    "url": "https://shipmail.to/book/acme/intro",
    "name": "Intro",
    "description": None,
    "duration_minutes": 30,
    "availability_days": [1, 2, 3, 4, 5],
    "window_start_minutes": 540,
    "window_end_minutes": 1020,
    "timezone": "America/New_York",
    "lock_timezone": False,
    "buffer_minutes": 0,
    "minimum_notice_minutes": 0,
    "max_advance_days": 30,
    "conferencing_provider": "zoom",
    "active": True,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z",
}


class TestCreate:
    def test_sends_post_booking_pages(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/booking-pages"
            body = json.loads(request.content)
            assert body["slug"] == "intro"
            assert body["conferencing_provider"] == "google_meet"
            assert body["lock_timezone"] is True
            return json_response(mock_page, 201)

        client = make_client(handler)
        page = client.booking_pages.create(
            {
                "name": "Intro",
                "mailbox": "orders@papertrail-studio.test",
                "slug": "intro",
                "duration_minutes": 30,
                "availability_days": [1, 2, 3, 4, 5],
                "window_start_minutes": 540,
                "window_end_minutes": 1020,
                "timezone": "America/New_York",
                "lock_timezone": True,
                "conferencing_provider": "google_meet",
            }
        )
        assert page["id"] == "bkp_1"
        assert page["conferencing_provider"] == "zoom"


class TestList:
    def test_sends_get_booking_pages(self) -> None:
        response = {"data": [mock_page], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/booking-pages"
            return json_response(response)

        client = make_client(handler)
        result = client.booking_pages.list()
        assert result["data"][0]["id"] == "bkp_1"


class TestGet:
    def test_sends_get_booking_pages_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/booking-pages/bkp_1"
            return json_response(mock_page)

        client = make_client(handler)
        page = client.booking_pages.get("bkp_1")
        assert page["id"] == "bkp_1"


mock_slots = {
    "object": "booking_page_slots",
    "booking_page_id": "bkp_1",
    "timezone": "Europe/Lisbon",
    "duration_minutes": 30,
    "from": "2026-11-09T00:00:00.000Z",
    "to": "2026-11-16T00:00:00.000Z",
    "slots": [{"start": "2026-11-09T09:00:00.000Z", "end": "2026-11-09T09:30:00.000Z"}],
}


def _slots_handler(request: httpx.Request) -> httpx.Response:
    assert request.method == "GET"
    assert request.url.path == "/v1/booking-pages/bkp_1/slots"
    assert request.url.params["from"] == "2026-11-09T00:00:00Z"
    assert "to" not in request.url.params
    return json_response(mock_slots)


class TestSlots:
    def test_sends_get_booking_pages_id_slots(self) -> None:
        client = make_client(_slots_handler)
        result = client.booking_pages.slots("bkp_1", {"from": "2026-11-09T00:00:00Z"})
        assert result["timezone"] == "Europe/Lisbon"
        assert result["slots"][0]["end"] == "2026-11-09T09:30:00.000Z"

    @pytest.mark.asyncio
    async def test_async_sends_get_booking_pages_id_slots(self) -> None:
        client = make_async_client(_slots_handler)
        result = await client.booking_pages.slots("bkp_1", {"from": "2026-11-09T00:00:00Z"})
        assert result["booking_page_id"] == "bkp_1"


class TestUpdate:
    def test_sends_patch_booking_pages_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/booking-pages/bkp_1"
            body = json.loads(request.content)
            assert body == {"conferencing_provider": None}
            return json_response({**mock_page, "conferencing_provider": None})

        client = make_client(handler)
        page = client.booking_pages.update("bkp_1", {"conferencing_provider": None})
        assert page["conferencing_provider"] is None


class TestDelete:
    def test_sends_delete_booking_pages_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/booking-pages/bkp_1"
            return httpx.Response(204)

        client = make_client(handler)
        assert client.booking_pages.delete("bkp_1") is None
