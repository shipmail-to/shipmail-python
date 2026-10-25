from __future__ import annotations

from typing import Literal, TypedDict

from .common import PaginationParams

CalendarEventStatus = Literal["confirmed", "tentative", "cancelled"]
CalendarFreeBusyStatus = Literal["free", "busy"]
CalendarEventPrivacy = Literal["public", "private", "secret"]
CalendarInvitationLanguage = Literal["en", "fr", "es"]
RecurrenceFrequency = Literal[
    "yearly", "monthly", "weekly", "daily", "hourly", "minutely", "secondly"
]
Weekday = Literal["mo", "tu", "we", "th", "fr", "sa", "su"]


class _RecurrenceNDayRequired(TypedDict):
    day: Weekday


class RecurrenceNDay(_RecurrenceNDayRequired, total=False):
    nth_of_period: int


class _RecurrenceRequired(TypedDict):
    frequency: RecurrenceFrequency


class Recurrence(_RecurrenceRequired, total=False):
    interval: int
    count: int
    until: str
    by_day: list[RecurrenceNDay]


class Reminder(TypedDict):
    minutes_before: int


class _CalendarAttendeeInputRequired(TypedDict):
    email: str


class CalendarAttendeeInput(_CalendarAttendeeInputRequired, total=False):
    name: str


class CalendarPerson(TypedDict):
    email: str
    name: str | None


class CalendarAttendee(CalendarPerson):
    status: Literal["needs-action", "accepted", "declined", "tentative"]


class CalendarInvitationOutcome(TypedDict):
    recipient: str
    status: Literal["sent", "failed", "unknown"]


class CalendarEvent(TypedDict):
    object: Literal["calendar_event"]
    id: str
    revision: str
    mailbox: str
    calendar_id: str | None
    uid: str | None
    title: str | None
    invitation_language: CalendarInvitationLanguage
    description: str | None
    location: str | None
    video_url: str | None
    all_day: bool
    start: str
    end: str
    timezone: str | None
    duration: str | None
    status: CalendarEventStatus | None
    free_busy_status: CalendarFreeBusyStatus | None
    privacy: CalendarEventPrivacy | None
    color: str | None
    recurrence: Recurrence | None
    recurrence_id: str | None
    reminders: list[Reminder]
    organizer: CalendarPerson | None
    attendees: list[CalendarAttendee]
    created_at: str | None
    updated_at: str | None


class CalendarEventMutationResult(CalendarEvent):
    invitation_outcomes: list[CalendarInvitationOutcome]
    invitation_failures: list[str]


class CalendarAvailabilitySlot(TypedDict):
    start: str
    end: str


# `from` is a Python keyword, so these dicts use the functional TypedDict syntax.
CalendarAvailability = TypedDict(
    "CalendarAvailability",
    {
        "object": Literal["calendar_availability"],
        "mailbox": str,
        "from": str,
        "to": str,
        "duration_minutes": int,
        "timezone": str,
        "slots": list[CalendarAvailabilitySlot],
    },
)

_ListCalendarEventsRequired = TypedDict(
    "_ListCalendarEventsRequired",
    {"mailbox": str, "from": str, "to": str},
)


class ListCalendarEventsParams(_ListCalendarEventsRequired, PaginationParams, total=False):
    expand: bool
    calendar_id: str


class GetCalendarEventParams(TypedDict):
    mailbox: str


class DeleteCalendarEventParams(TypedDict):
    mailbox: str


class _CreateCalendarEventRequired(TypedDict):
    mailbox: str
    title: str
    start: str


class CreateCalendarEventParams(_CreateCalendarEventRequired, total=False):
    operation_key: str
    send_invitations: bool
    calendar_id: str
    invitation_language: CalendarInvitationLanguage
    description: str
    timezone: str
    duration: str
    all_day: bool
    location: str
    video_url: str
    color: str
    status: CalendarEventStatus
    free_busy_status: CalendarFreeBusyStatus
    privacy: CalendarEventPrivacy
    recurrence: Recurrence
    reminders: list[Reminder]
    attendees: list[CalendarAttendeeInput]


class _UpdateCalendarEventRequired(TypedDict):
    mailbox: str


class UpdateCalendarEventParams(_UpdateCalendarEventRequired, total=False):
    operation_key: str
    expected_revision: str
    send_guest_updates: bool
    title: str
    invitation_language: CalendarInvitationLanguage
    description: str | None
    start: str
    timezone: str | None
    duration: str
    all_day: bool
    location: str | None
    video_url: str | None
    color: str
    status: CalendarEventStatus
    free_busy_status: CalendarFreeBusyStatus
    privacy: CalendarEventPrivacy
    recurrence: Recurrence | None
    reminders: list[Reminder] | None
    attendees: list[CalendarAttendeeInput]


_CalendarAvailabilityRequired = TypedDict(
    "_CalendarAvailabilityRequired",
    {"mailbox": str, "from": str, "to": str},
)


class CalendarAvailabilityParams(_CalendarAvailabilityRequired, total=False):
    duration: int
    interval: int
    timezone: str
    days: list[int]
    window_start: int
    window_end: int
    buffer: int
    minimum_notice: int
