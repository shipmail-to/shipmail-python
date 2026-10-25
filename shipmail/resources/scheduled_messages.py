from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions
    from .._types.message import (
        ListScheduledMessagesParams,
        ScheduledMessage,
        ScheduledMessageList,
        UpdateScheduledMessageParams,
    )


class SyncScheduledMessages:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(
        self,
        params: ListScheduledMessagesParams | None = None,
        options: MethodOptions | None = None,
    ) -> ScheduledMessageList:
        query = params or {}
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/scheduled-messages",
                query={
                    "include_held": query.get("include_held"),
                    "search": query.get("search"),
                    "limit": query.get("limit"),
                },
                method_options=options,
            )
        )

    def get(self, id: str, options: MethodOptions | None = None) -> ScheduledMessage:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/scheduled-messages/{quote(id, safe='')}",
                method_options=options,
            )
        )

    def update(
        self,
        id: str,
        params: UpdateScheduledMessageParams,
        options: MethodOptions | None = None,
    ) -> ScheduledMessage:
        return self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/scheduled-messages/{quote(id, safe='')}",
                body=params,
                method_options=options,
            )
        )

    def cancel(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/scheduled-messages/{quote(id, safe='')}",
                method_options=options,
            )
        )


class AsyncScheduledMessages:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(
        self,
        params: ListScheduledMessagesParams | None = None,
        options: MethodOptions | None = None,
    ) -> ScheduledMessageList:
        query = params or {}
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/scheduled-messages",
                query={
                    "include_held": query.get("include_held"),
                    "search": query.get("search"),
                    "limit": query.get("limit"),
                },
                method_options=options,
            )
        )

    async def get(self, id: str, options: MethodOptions | None = None) -> ScheduledMessage:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/scheduled-messages/{quote(id, safe='')}",
                method_options=options,
            )
        )

    async def update(
        self,
        id: str,
        params: UpdateScheduledMessageParams,
        options: MethodOptions | None = None,
    ) -> ScheduledMessage:
        return await self._client.request(
            RequestOptions(
                method="PATCH",
                path=f"/scheduled-messages/{quote(id, safe='')}",
                body=params,
                method_options=options,
            )
        )

    async def cancel(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(
                method="DELETE",
                path=f"/scheduled-messages/{quote(id, safe='')}",
                method_options=options,
            )
        )
