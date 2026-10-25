from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.message import Message
    from .._types.thread import GetThreadParams, ListThreadsParams, ReplyToThreadParams


class SyncThreads:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(self, params: ListThreadsParams, options: MethodOptions | None = None) -> PaginatedResponse:
        return self._client.request(RequestOptions(
            method="GET",
            path="/threads",
            query={
                "mailbox_id": params.get("mailbox_id"),
                "cursor": params.get("cursor"),
                "limit": params.get("limit"),
            },
            method_options=options,
        ))

    def list_auto_paginating(self, *, mailbox_id: str, limit: int | None = None) -> SyncPage[Any]:
        return SyncPage(self._client, "/threads", {"mailbox_id": mailbox_id, "limit": limit})

    def get(self, id: str, params: GetThreadParams, options: MethodOptions | None = None) -> PaginatedResponse:
        return self._client.request(RequestOptions(
            method="GET",
            path=f"/threads/{quote(id, safe='')}",
            query={
                "mailbox_id": params.get("mailbox_id"),
                "cursor": params.get("cursor"),
                "limit": params.get("limit"),
            },
            method_options=options,
        ))

    def reply(self, id: str, params: ReplyToThreadParams, options: MethodOptions | None = None) -> Message:
        return self._client.request(RequestOptions(method="POST", path=f"/threads/{quote(id, safe='')}/reply", body=params, method_options=options))


class AsyncThreads:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(self, params: ListThreadsParams, options: MethodOptions | None = None) -> PaginatedResponse:
        return await self._client.request(RequestOptions(
            method="GET",
            path="/threads",
            query={
                "mailbox_id": params.get("mailbox_id"),
                "cursor": params.get("cursor"),
                "limit": params.get("limit"),
            },
            method_options=options,
        ))

    def list_auto_paginating(self, *, mailbox_id: str, limit: int | None = None) -> AsyncPage[Any]:
        return AsyncPage(self._client, "/threads", {"mailbox_id": mailbox_id, "limit": limit})

    async def get(self, id: str, params: GetThreadParams, options: MethodOptions | None = None) -> PaginatedResponse:
        return await self._client.request(RequestOptions(
            method="GET",
            path=f"/threads/{quote(id, safe='')}",
            query={
                "mailbox_id": params.get("mailbox_id"),
                "cursor": params.get("cursor"),
                "limit": params.get("limit"),
            },
            method_options=options,
        ))

    async def reply(self, id: str, params: ReplyToThreadParams, options: MethodOptions | None = None) -> Message:
        return await self._client.request(RequestOptions(method="POST", path=f"/threads/{quote(id, safe='')}/reply", body=params, method_options=options))
