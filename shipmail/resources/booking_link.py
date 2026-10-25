from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.booking_link import (
        BookingLink,
        BookingLinkStatus,
        CreateBookingLinkParams,
        ListBookingLinksParams,
        UpdateBookingLinkParams,
    )
    from .._types.common import MethodOptions, PaginatedResponse


def _link(link_id: str) -> str:
    return f"/booking-links/{quote(link_id, safe='')}"


def _list_query(params: ListBookingLinksParams | None) -> dict[str, str | int | bool | None]:
    return {
        "cursor": params.get("cursor") if params else None,
        "limit": params.get("limit") if params else None,
        "status": params.get("status") if params else None,
    }


class SyncBookingLinks:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(
        self, params: CreateBookingLinkParams, options: MethodOptions | None = None
    ) -> BookingLink:
        return self._client.request(
            RequestOptions(method="POST", path="/booking-links", body=params, method_options=options)
        )

    def list(
        self, params: ListBookingLinksParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/booking-links",
                query=_list_query(params),
                method_options=options,
            )
        )

    def list_auto_paginating(
        self, *, limit: int | None = None, status: BookingLinkStatus | None = None
    ) -> SyncPage[BookingLink]:
        return SyncPage(self._client, "/booking-links", {"limit": limit, "status": status})

    def get(self, id: str, options: MethodOptions | None = None) -> BookingLink:
        return self._client.request(
            RequestOptions(method="GET", path=_link(id), method_options=options)
        )

    def update(
        self, id: str, params: UpdateBookingLinkParams, options: MethodOptions | None = None
    ) -> BookingLink:
        return self._client.request(
            RequestOptions(method="PATCH", path=_link(id), body=params, method_options=options)
        )

    def revoke(self, id: str, options: MethodOptions | None = None) -> BookingLink:
        """Revoke a link. The link stays readable; revoking cannot be undone."""
        return self._client.request(
            RequestOptions(method="POST", path=f"{_link(id)}/revoke", method_options=options)
        )


class AsyncBookingLinks:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(
        self, params: CreateBookingLinkParams, options: MethodOptions | None = None
    ) -> BookingLink:
        return await self._client.request(
            RequestOptions(method="POST", path="/booking-links", body=params, method_options=options)
        )

    async def list(
        self, params: ListBookingLinksParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/booking-links",
                query=_list_query(params),
                method_options=options,
            )
        )

    def list_auto_paginating(
        self, *, limit: int | None = None, status: BookingLinkStatus | None = None
    ) -> AsyncPage[BookingLink]:
        return AsyncPage(self._client, "/booking-links", {"limit": limit, "status": status})

    async def get(self, id: str, options: MethodOptions | None = None) -> BookingLink:
        return await self._client.request(
            RequestOptions(method="GET", path=_link(id), method_options=options)
        )

    async def update(
        self, id: str, params: UpdateBookingLinkParams, options: MethodOptions | None = None
    ) -> BookingLink:
        return await self._client.request(
            RequestOptions(method="PATCH", path=_link(id), body=params, method_options=options)
        )

    async def revoke(self, id: str, options: MethodOptions | None = None) -> BookingLink:
        """Revoke a link. The link stays readable; revoking cannot be undone."""
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_link(id)}/revoke", method_options=options)
        )
