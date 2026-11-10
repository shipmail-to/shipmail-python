from __future__ import annotations

from typing import Literal, TypedDict

from .common import PaginationParams

ConferencingProviderId = Literal["zoom", "google_meet"]


class BookingPage(TypedDict):
    object: Literal["booking_page"]
    id: str
    mailbox: str
    slug: str
    url: str | None
    name: str
    description: str | None
    duration_minutes: int
    availability_days: list[int]
    window_start_minutes: int
    window_end_minutes: int
    timezone: str
    lock_timezone: bool
    buffer_minutes: int
    minimum_notice_minutes: int
    max_advance_days: int
    conferencing_provider: ConferencingProviderId | None
    active: bool
    created_at: str
    updated_at: str


ListBookingPagesParams = PaginationParams


class _CreateBookingPageRequired(TypedDict):
    name: str
    mailbox: str
    slug: str
    duration_minutes: int
    availability_days: list[int]
    window_start_minutes: int
    window_end_minutes: int
    timezone: str


class CreateBookingPageParams(_CreateBookingPageRequired, total=False):
    description: str | None
    lock_timezone: bool
    buffer_minutes: int
    minimum_notice_minutes: int
    max_advance_days: int
    conferencing_provider: ConferencingProviderId | None
    active: bool


class UpdateBookingPageParams(TypedDict, total=False):
    name: str
    mailbox: str
    slug: str
    duration_minutes: int
    availability_days: list[int]
    window_start_minutes: int
    window_end_minutes: int
    timezone: str
    lock_timezone: bool
    description: str | None
    buffer_minutes: int
    minimum_notice_minutes: int
    max_advance_days: int
    conferencing_provider: ConferencingProviderId | None
    active: bool


class BookingPageSlot(TypedDict):
    start: str
    end: str


BookingPageSlots = TypedDict(
    "BookingPageSlots",
    {
        "object": Literal["booking_page_slots"],
        "booking_page_id": str,
        "timezone": str,
        "duration_minutes": int,
        "from": str,
        "to": str,
        "slots": list[BookingPageSlot],
    },
)

# ISO 8601 instants. "from" defaults to now, "to" to the end of the page's booking horizon.
GetBookingPageSlotsParams = TypedDict(
    "GetBookingPageSlotsParams", {"from": str, "to": str}, total=False
)
