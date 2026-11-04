from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.event_queue import (
        AckEventQueueEventsResponse,
        CreateEventQueueParams,
        EventQueue,
        EventQueueEvents,
        ListEventQueueEventsParams,
        ListEventQueuesParams,
    )


class SyncEventQueues:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(self, params: CreateEventQueueParams, options: MethodOptions | None = None) -> EventQueue:
        return self._client.request(
            RequestOptions(method="POST", path="/event-queues", body=params, method_options=options)
        )

    def list(
        self, params: ListEventQueuesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/event-queues",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[EventQueue]:
        return SyncPage(self._client, "/event-queues", {"limit": limit})

    def get(self, id: str, options: MethodOptions | None = None) -> EventQueue:
        return self._client.request(
            RequestOptions(method="GET", path=f"/event-queues/{quote(id, safe='')}", method_options=options)
        )

    def delete(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(method="DELETE", path=f"/event-queues/{quote(id, safe='')}", method_options=options)
        )

    def list_events(
        self, id: str, params: ListEventQueueEventsParams | None = None, options: MethodOptions | None = None
    ) -> EventQueueEvents:
        """Read the oldest unacknowledged events. Reading changes nothing; acknowledge them with ``ack``."""
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/event-queues/{quote(id, safe='')}/events",
                query={"limit": params.get("limit") if params else None},
                method_options=options,
            )
        )

    def ack(
        self, id: str, event_ids: Sequence[str], options: MethodOptions | None = None
    ) -> AckEventQueueEventsResponse:
        """Delete handled events by their envelope ``event_id``. Idempotent."""
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/event-queues/{quote(id, safe='')}/events/ack",
                body={"event_ids": list(event_ids)},
                method_options=options,
            )
        )


class AsyncEventQueues:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(self, params: CreateEventQueueParams, options: MethodOptions | None = None) -> EventQueue:
        return await self._client.request(
            RequestOptions(method="POST", path="/event-queues", body=params, method_options=options)
        )

    async def list(
        self, params: ListEventQueuesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/event-queues",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[EventQueue]:
        return AsyncPage(self._client, "/event-queues", {"limit": limit})

    async def get(self, id: str, options: MethodOptions | None = None) -> EventQueue:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/event-queues/{quote(id, safe='')}", method_options=options)
        )

    async def delete(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(method="DELETE", path=f"/event-queues/{quote(id, safe='')}", method_options=options)
        )

    async def list_events(
        self, id: str, params: ListEventQueueEventsParams | None = None, options: MethodOptions | None = None
    ) -> EventQueueEvents:
        """Read the oldest unacknowledged events. Reading changes nothing; acknowledge them with ``ack``."""
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/event-queues/{quote(id, safe='')}/events",
                query={"limit": params.get("limit") if params else None},
                method_options=options,
            )
        )

    async def ack(
        self, id: str, event_ids: Sequence[str], options: MethodOptions | None = None
    ) -> AckEventQueueEventsResponse:
        """Delete handled events by their envelope ``event_id``. Idempotent."""
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/event-queues/{quote(id, safe='')}/events/ack",
                body={"event_ids": list(event_ids)},
                method_options=options,
            )
        )
