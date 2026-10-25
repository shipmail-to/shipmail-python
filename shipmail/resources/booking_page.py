from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.booking_page import (
        BookingPage,
        CreateBookingPageParams,
        ListBookingPagesParams,
        UpdateBookingPageParams,
    )
    from .._types.common import MethodOptions, PaginatedResponse


def _page(page_id: str) -> str:
    return f"/booking-pages/{quote(page_id, safe='')}"


class SyncBookingPages:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(
        self, params: CreateBookingPageParams, options: MethodOptions | None = None
    ) -> BookingPage:
        return self._client.request(
            RequestOptions(method="POST", path="/booking-pages", body=params, method_options=options)
        )

    def list(
        self, params: ListBookingPagesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/booking-pages",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[BookingPage]:
        return SyncPage(self._client, "/booking-pages", {"limit": limit})

    def get(self, id: str, options: MethodOptions | None = None) -> BookingPage:
        return self._client.request(
            RequestOptions(method="GET", path=_page(id), method_options=options)
        )

    def update(
        self, id: str, params: UpdateBookingPageParams, options: MethodOptions | None = None
    ) -> BookingPage:
        return self._client.request(
            RequestOptions(method="PATCH", path=_page(id), body=params, method_options=options)
        )

    def delete(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(RequestOptions(method="DELETE", path=_page(id), method_options=options))


class AsyncBookingPages:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(
        self, params: CreateBookingPageParams, options: MethodOptions | None = None
    ) -> BookingPage:
        return await self._client.request(
            RequestOptions(method="POST", path="/booking-pages", body=params, method_options=options)
        )

    async def list(
        self, params: ListBookingPagesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/booking-pages",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[BookingPage]:
        return AsyncPage(self._client, "/booking-pages", {"limit": limit})

    async def get(self, id: str, options: MethodOptions | None = None) -> BookingPage:
        return await self._client.request(
            RequestOptions(method="GET", path=_page(id), method_options=options)
        )

    async def update(
        self, id: str, params: UpdateBookingPageParams, options: MethodOptions | None = None
    ) -> BookingPage:
        return await self._client.request(
            RequestOptions(method="PATCH", path=_page(id), body=params, method_options=options)
        )

    async def delete(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(method="DELETE", path=_page(id), method_options=options)
        )
