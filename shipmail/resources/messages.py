from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.message import (
        ListMessageAnalyticsParams,
        ListMessagesParams,
        Message,
        MessageAnalyticsPage,
        ReplyToMessageParams,
        SendMessageParams,
    )


class SyncMessages:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def send(self, params: SendMessageParams, options: MethodOptions | None = None) -> Message:
        return self._client.request(
            RequestOptions(method="POST", path="/messages", body=params, method_options=options)
        )

    def list(self, params: ListMessagesParams, options: MethodOptions | None = None) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/messages",
                query={
                    "mailbox_id": params.get("mailbox_id"),
                    "client_reference": params.get("client_reference"),
                    "cursor": params.get("cursor"),
                    "limit": params.get("limit"),
                },
                method_options=options,
            )
        )

    def list_auto_paginating(
        self,
        *,
        mailbox_id: str | None = None,
        client_reference: str | None = None,
        limit: int | None = None,
    ) -> SyncPage[Any]:
        return SyncPage(
            self._client,
            "/messages",
            {
                "mailbox_id": mailbox_id,
                "client_reference": client_reference,
                "limit": limit,
            },
        )

    def list_analytics(
        self,
        params: ListMessageAnalyticsParams | None = None,
        options: MethodOptions | None = None,
    ) -> MessageAnalyticsPage:
        params = params or {}
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/messages/analytics",
                query={
                    "updated_after": params.get("updated_after"),
                    "updated_before": params.get("updated_before"),
                    "cursor": params.get("cursor"),
                    "limit": params.get("limit"),
                },
                method_options=options,
            )
        )

    def get(self, id: str, options: MethodOptions | None = None) -> Message:
        return self._client.request(
            RequestOptions(method="GET", path=f"/messages/{quote(id, safe='')}", method_options=options)
        )

    def reply(self, id: str, params: ReplyToMessageParams, options: MethodOptions | None = None) -> Message:
        return self._client.request(
            RequestOptions(
                method="POST", path=f"/messages/{quote(id, safe='')}/reply", body=params, method_options=options
            )
        )


class AsyncMessages:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def send(self, params: SendMessageParams, options: MethodOptions | None = None) -> Message:
        return await self._client.request(
            RequestOptions(method="POST", path="/messages", body=params, method_options=options)
        )

    async def list(self, params: ListMessagesParams, options: MethodOptions | None = None) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/messages",
                query={
                    "mailbox_id": params.get("mailbox_id"),
                    "client_reference": params.get("client_reference"),
                    "cursor": params.get("cursor"),
                    "limit": params.get("limit"),
                },
                method_options=options,
            )
        )

    def list_auto_paginating(
        self,
        *,
        mailbox_id: str | None = None,
        client_reference: str | None = None,
        limit: int | None = None,
    ) -> AsyncPage[Any]:
        return AsyncPage(
            self._client,
            "/messages",
            {
                "mailbox_id": mailbox_id,
                "client_reference": client_reference,
                "limit": limit,
            },
        )

    async def list_analytics(
        self,
        params: ListMessageAnalyticsParams | None = None,
        options: MethodOptions | None = None,
    ) -> MessageAnalyticsPage:
        params = params or {}
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/messages/analytics",
                query={
                    "updated_after": params.get("updated_after"),
                    "updated_before": params.get("updated_before"),
                    "cursor": params.get("cursor"),
                    "limit": params.get("limit"),
                },
                method_options=options,
            )
        )

    async def get(self, id: str, options: MethodOptions | None = None) -> Message:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/messages/{quote(id, safe='')}", method_options=options)
        )

    async def reply(self, id: str, params: ReplyToMessageParams, options: MethodOptions | None = None) -> Message:
        return await self._client.request(
            RequestOptions(
                method="POST", path=f"/messages/{quote(id, safe='')}/reply", body=params, method_options=options
            )
        )
