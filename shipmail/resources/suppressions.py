from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.suppression import CreateSuppressionParams, ListSuppressionsParams, Suppression, SuppressionScope


class SyncSuppressions:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(self, params: CreateSuppressionParams, options: MethodOptions | None = None) -> Suppression:
        return self._client.request(RequestOptions(method="POST", path="/suppressions", body=params, method_options=options))

    def list(self, params: ListSuppressionsParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return self._client.request(RequestOptions(
            method="GET",
            path="/suppressions",
            query={
                "cursor": params.get("cursor") if params else None,
                "limit": params.get("limit") if params else None,
                "scope": params.get("scope") if params else None,
            },
            method_options=options,
        ))

    def list_auto_paginating(
        self, *, limit: int | None = None, scope: SuppressionScope | None = None
    ) -> SyncPage[Suppression]:
        return SyncPage(self._client, "/suppressions", {"limit": limit, "scope": scope})

    def remove(self, email: str, options: MethodOptions | None = None) -> None:
        self._client.request(RequestOptions(method="DELETE", path=f"/suppressions/{quote(email, safe='')}", method_options=options))


class AsyncSuppressions:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(self, params: CreateSuppressionParams, options: MethodOptions | None = None) -> Suppression:
        return await self._client.request(RequestOptions(method="POST", path="/suppressions", body=params, method_options=options))

    async def list(self, params: ListSuppressionsParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return await self._client.request(RequestOptions(
            method="GET",
            path="/suppressions",
            query={
                "cursor": params.get("cursor") if params else None,
                "limit": params.get("limit") if params else None,
                "scope": params.get("scope") if params else None,
            },
            method_options=options,
        ))

    def list_auto_paginating(
        self, *, limit: int | None = None, scope: SuppressionScope | None = None
    ) -> AsyncPage[Suppression]:
        return AsyncPage(self._client, "/suppressions", {"limit": limit, "scope": scope})

    async def remove(self, email: str, options: MethodOptions | None = None) -> None:
        await self._client.request(RequestOptions(method="DELETE", path=f"/suppressions/{quote(email, safe='')}", method_options=options))
