from __future__ import annotations

from typing import Literal, TypedDict

from .booking_page import ConferencingProviderId
from .common import PaginationParams

BookingLinkStatus = Literal["open", "booked", "expired", "revoked"]


class BookingLinkRange(TypedDict):
    start: str
    end: str


class BookingLink(TypedDict):
    object: Literal["booking_link"]
    id: str
    mailbox: str
    slug: str
    url: str | None
    name: str
    description: str | None
    duration_minutes: int
    timezone: str
    offered_ranges: list[BookingLinkRange] | None
    source_page_id: str | None
    buffer_minutes: int
    minimum_notice_minutes: int
    conferencing_provider: ConferencingProviderId | None
    max_bookings: int | None
    bookings_count: int
    expires_at: str | None
    status: BookingLinkStatus
    created_at: str


class ListBookingLinksParams(PaginationParams, total=False):
    status: BookingLinkStatus


class _CreateBookingLinkRequired(TypedDict):
    name: str
    mailbox: str
    duration_minutes: int
    timezone: str


class CreateBookingLinkParams(_CreateBookingLinkRequired, total=False):
    offered_ranges: list[BookingLinkRange]
    source_page_id: str | None
    description: str | None
    buffer_minutes: int
    minimum_notice_minutes: int
    conferencing_provider: ConferencingProviderId | None
    max_bookings: int | None
    expires_at: str | None


class UpdateBookingLinkParams(TypedDict, total=False):
    name: str
    mailbox: str
    duration_minutes: int
    timezone: str
    offered_ranges: list[BookingLinkRange] | None
    source_page_id: str | None
    description: str | None
    buffer_minutes: int
    minimum_notice_minutes: int
    conferencing_provider: ConferencingProviderId | None
    max_bookings: int | None
    expires_at: str | None
