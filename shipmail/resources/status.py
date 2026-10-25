from __future__ import annotations

from typing import TYPE_CHECKING

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, StatusResponse


class SyncStatus:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def get(self, options: MethodOptions | None = None) -> StatusResponse:
        return self._client.request(RequestOptions(method="GET", path="/status", method_options=options))


class AsyncStatus:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def get(self, options: MethodOptions | None = None) -> StatusResponse:
        return await self._client.request(RequestOptions(method="GET", path="/status", method_options=options))
