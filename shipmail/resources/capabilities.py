from __future__ import annotations

from typing import TYPE_CHECKING

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.capabilities import CapabilitiesResponse
    from .._types.common import MethodOptions


class SyncCapabilities:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def get(self, options: MethodOptions | None = None) -> CapabilitiesResponse:
        return self._client.request(RequestOptions(method="GET", path="/capabilities", method_options=options))


class AsyncCapabilities:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def get(self, options: MethodOptions | None = None) -> CapabilitiesResponse:
        return await self._client.request(RequestOptions(method="GET", path="/capabilities", method_options=options))
