from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions
    from .._types.reply_scan import (
        CreateReplyScanParams,
        ListReplyScanResultsParams,
        ReplyScan,
        ReplyScanResults,
    )


class SyncReplyScans:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(self, params: CreateReplyScanParams, options: MethodOptions | None = None) -> ReplyScan:
        return self._client.request(
            RequestOptions(method="POST", path="/reply-scans", body=params, method_options=options)
        )

    def get(self, id: str, options: MethodOptions | None = None) -> ReplyScan:
        return self._client.request(
            RequestOptions(method="GET", path=f"/reply-scans/{quote(id, safe='')}", method_options=options)
        )

    def list_results(
        self,
        id: str,
        params: ListReplyScanResultsParams | None = None,
        options: MethodOptions | None = None,
    ) -> ReplyScanResults:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/reply-scans/{quote(id, safe='')}/results",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )


class AsyncReplyScans:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(self, params: CreateReplyScanParams, options: MethodOptions | None = None) -> ReplyScan:
        return await self._client.request(
            RequestOptions(method="POST", path="/reply-scans", body=params, method_options=options)
        )

    async def get(self, id: str, options: MethodOptions | None = None) -> ReplyScan:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/reply-scans/{quote(id, safe='')}", method_options=options)
        )

    async def list_results(
        self,
        id: str,
        params: ListReplyScanResultsParams | None = None,
        options: MethodOptions | None = None,
    ) -> ReplyScanResults:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/reply-scans/{quote(id, safe='')}/results",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )
