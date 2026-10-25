from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.member import ListMembersParams, Member


class SyncMembers:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(self, params: ListMembersParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/members",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[Member]:
        return SyncPage(self._client, "/members", {"limit": limit})

    def get(self, id: str, options: MethodOptions | None = None) -> Member:
        return self._client.request(
            RequestOptions(method="GET", path=f"/members/{quote(id, safe='')}", method_options=options)
        )

class AsyncMembers:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(
        self, params: ListMembersParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/members",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[Member]:
        return AsyncPage(self._client, "/members", {"limit": limit})

    async def get(self, id: str, options: MethodOptions | None = None) -> Member:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/members/{quote(id, safe='')}", method_options=options)
        )
