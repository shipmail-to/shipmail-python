from __future__ import annotations

import json

import httpx

from tests.conftest import json_response, make_client

ADDRESS = "orders@papertrail-studio.test"

mock_event = {
    "object": "calendar_event",
    "id": "evt_1",
    "revision": "a" * 64,
    "mailbox": ADDRESS,
    "calendar_id": "cal_1",
    "uid": "uid-1",
    "title": "Sync",
    "invitation_language": "fr",
    "description": None,
    "location": None,
    "video_url": None,
    "all_day": False,
    "start": "2026-08-01T14:00:00Z",
    "end": "2026-08-01T14:30:00Z",
    "timezone": "Europe/Paris",
    "duration": "PT30M",
    "status": "confirmed",
    "free_busy_status": "busy",
    "privacy": None,
    "color": None,
    "recurrence": None,
    "recurrence_id": None,
    "reminders": [],
    "organizer": {"email": ADDRESS, "name": "Orders"},
    "attendees": [{"email": "guest@example.com", "name": "Guest", "status": "needs-action"}],
    "created_at": None,
    "updated_at": None,
}

mock_mutation_event = {
    **mock_event,
    "invitation_outcomes": [],
    "invitation_failures": [],
}


class TestCreate:
    def test_sends_post_events_with_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/calendar/events"
            body = json.loads(request.content)
            assert body == {
                "mailbox": ADDRESS,
                "operation_key": "calendar-create-0001",
                "send_invitations": False,
                "title": "Sync",
                "invitation_language": "fr",
                "start": "2026-08-01T14:00:00",
                "attendees": [{"email": "guest@example.com", "name": "Guest"}],
            }
            return json_response(mock_mutation_event, 201)

        client = make_client(handler)
        event = client.calendar.events.create(
            {
                "mailbox": ADDRESS,
                "operation_key": "calendar-create-0001",
                "send_invitations": False,
                "title": "Sync",
                "invitation_language": "fr",
                "start": "2026-08-01T14:00:00",
                "attendees": [{"email": "guest@example.com", "name": "Guest"}],
            }
        )
        assert event["id"] == "evt_1"


class TestList:
    def test_forwards_mailbox_from_to(self) -> None:
        response = {"data": [mock_event], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/calendar/events"
            assert str(request.url.params.get("mailbox")) == ADDRESS
            assert str(request.url.params.get("from")) == "2026-08-01T00:00:00Z"
            assert str(request.url.params.get("to")) == "2026-08-08T00:00:00Z"
            return json_response(response)

        client = make_client(handler)
        result = client.calendar.events.list(
            {"mailbox": ADDRESS, "from": "2026-08-01T00:00:00Z", "to": "2026-08-08T00:00:00Z"}
        )
        assert result["data"][0]["id"] == "evt_1"


class TestGet:
    def test_forwards_mailbox_query(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/calendar/events/evt_1"
            assert str(request.url.params.get("mailbox")) == ADDRESS
            return json_response(mock_event)

        client = make_client(handler)
        event = client.calendar.events.get("evt_1", {"mailbox": ADDRESS})
        assert event["id"] == "evt_1"


class TestUpdate:
    def test_sends_patch_with_null_to_clear(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/calendar/events/evt_1"
            body = json.loads(request.content)
            assert body == {
                "mailbox": ADDRESS,
                "operation_key": "calendar-update-0001",
                "expected_revision": "a" * 64,
                "send_guest_updates": False,
                "invitation_language": "es",
                "location": None,
            }
            return json_response(mock_mutation_event)

        client = make_client(handler)
        client.calendar.events.update(
            "evt_1",
            {
                "mailbox": ADDRESS,
                "operation_key": "calendar-update-0001",
                "expected_revision": "a" * 64,
                "send_guest_updates": False,
                "invitation_language": "es",
                "location": None,
            },
        )


class TestDelete:
    def test_sends_delete_with_mailbox(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/calendar/events/evt_1"
            assert str(request.url.params.get("mailbox")) == ADDRESS
            return httpx.Response(204)

        client = make_client(handler)
        assert client.calendar.events.delete("evt_1", {"mailbox": ADDRESS}) is None


class TestAvailability:
    def test_joins_days_and_returns_slots(self) -> None:
        availability = {
            "object": "calendar_availability",
            "mailbox": ADDRESS,
            "from": "2026-08-03T00:00:00Z",
            "to": "2026-08-04T00:00:00Z",
            "duration_minutes": 30,
            "timezone": "America/New_York",
            "slots": [{"start": "2026-08-03T13:00:00.000Z", "end": "2026-08-03T13:30:00.000Z"}],
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/calendar/availability"
            assert str(request.url.params.get("days")) == "1,3,5"
            assert str(request.url.params.get("duration")) == "30"
            return json_response(availability)

        client = make_client(handler)
        result = client.calendar.availability(
            {
                "mailbox": ADDRESS,
                "from": "2026-08-03T00:00:00Z",
                "to": "2026-08-04T00:00:00Z",
                "duration": 30,
                "days": [1, 3, 5],
            }
        )
        assert result["object"] == "calendar_availability"
        assert len(result["slots"]) == 1
