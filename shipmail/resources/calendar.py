from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.calendar import (
        CalendarAvailability,
        CalendarAvailabilityParams,
        CalendarEvent,
        CalendarEventMutationResult,
        CreateCalendarEventParams,
        DeleteCalendarEventParams,
        GetCalendarEventParams,
        ListCalendarEventsParams,
        UpdateCalendarEventParams,
    )
    from .._types.common import MethodOptions, PaginatedResponse


def _event(event_id: str) -> str:
    return f"/calendar/events/{quote(event_id, safe='')}"


def _availability_query(params: CalendarAvailabilityParams) -> dict[str, str | int | bool | None]:
    days = params.get("days")
    return {
        "mailbox": params["mailbox"],
        "from": params["from"],
        "to": params["to"],
        "duration": params.get("duration"),
        "interval": params.get("interval"),
        "timezone": params.get("timezone"),
        "days": ",".join(str(d) for d in days) if days is not None else None,
        "window_start": params.get("window_start"),
        "window_end": params.get("window_end"),
        "buffer": params.get("buffer"),
        "minimum_notice": params.get("minimum_notice"),
    }


def _list_query(params: ListCalendarEventsParams) -> dict[str, str | int | bool | None]:
    return {
        "mailbox": params["mailbox"],
        "from": params["from"],
        "to": params["to"],
        "expand": params.get("expand"),
        "calendar_id": params.get("calendar_id"),
        "cursor": params.get("cursor"),
        "limit": params.get("limit"),
    }


class SyncCalendarEvents:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(
        self, params: CreateCalendarEventParams, options: MethodOptions | None = None
    ) -> CalendarEventMutationResult:
        return self._client.request(
            RequestOptions(method="POST", path="/calendar/events", body=params, method_options=options)
        )

    def list(
        self, params: ListCalendarEventsParams, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET", path="/calendar/events", query=_list_query(params), method_options=options
            )
        )

    def list_auto_paginating(self, params: ListCalendarEventsParams) -> SyncPage[CalendarEvent]:
        query = _list_query(params)
        query.pop("cursor", None)
        return SyncPage(self._client, "/calendar/events", query)

    def get(
        self, id: str, params: GetCalendarEventParams, options: MethodOptions | None = None
    ) -> CalendarEvent:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=_event(id),
                query={"mailbox": params["mailbox"]},
                method_options=options,
            )
        )

    def update(
        self, id: str, params: UpdateCalendarEventParams, options: MethodOptions | None = None
    ) -> CalendarEventMutationResult:
        return self._client.request(
            RequestOptions(method="PATCH", path=_event(id), body=params, method_options=options)
        )

    def delete(
        self, id: str, params: DeleteCalendarEventParams, options: MethodOptions | None = None
    ) -> None:
        self._client.request(
            RequestOptions(
                method="DELETE",
                path=_event(id),
                query={"mailbox": params["mailbox"]},
                method_options=options,
            )
        )


class SyncCalendar:
    events: SyncCalendarEvents

    def __init__(self, client: Shipmail) -> None:
        self._client = client
        self.events = SyncCalendarEvents(client)

    def availability(
        self, params: CalendarAvailabilityParams, options: MethodOptions | None = None
    ) -> CalendarAvailability:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/calendar/availability",
                query=_availability_query(params),
                method_options=options,
            )
        )


class AsyncCalendarEvents:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(
        self, params: CreateCalendarEventParams, options: MethodOptions | None = None
    ) -> CalendarEventMutationResult:
        return await self._client.request(
            RequestOptions(method="POST", path="/calendar/events", body=params, method_options=options)
        )

    async def list(
        self, params: ListCalendarEventsParams, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET", path="/calendar/events", query=_list_query(params), method_options=options
            )
        )

    def list_auto_paginating(self, params: ListCalendarEventsParams) -> AsyncPage[CalendarEvent]:
        query = _list_query(params)
        query.pop("cursor", None)
        return AsyncPage(self._client, "/calendar/events", query)

    async def get(
        self, id: str, params: GetCalendarEventParams, options: MethodOptions | None = None
    ) -> CalendarEvent:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=_event(id),
                query={"mailbox": params["mailbox"]},
                method_options=options,
            )
        )

    async def update(
        self, id: str, params: UpdateCalendarEventParams, options: MethodOptions | None = None
    ) -> CalendarEventMutationResult:
        return await self._client.request(
            RequestOptions(method="PATCH", path=_event(id), body=params, method_options=options)
        )

    async def delete(
        self, id: str, params: DeleteCalendarEventParams, options: MethodOptions | None = None
    ) -> None:
        await self._client.request(
            RequestOptions(
                method="DELETE",
                path=_event(id),
                query={"mailbox": params["mailbox"]},
                method_options=options,
            )
        )


class AsyncCalendar:
    events: AsyncCalendarEvents

    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client
        self.events = AsyncCalendarEvents(client)

    async def availability(
        self, params: CalendarAvailabilityParams, options: MethodOptions | None = None
    ) -> CalendarAvailability:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/calendar/availability",
                query=_availability_query(params),
                method_options=options,
            )
        )
