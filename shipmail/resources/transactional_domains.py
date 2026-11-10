from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions
    from .._types.transactional import (
        CreateTransactionalDomainParams,
        TransactionalDomain,
        TransactionalDomainList,
    )


def _path(id: str) -> str:
    return f"/transactional-domains/{quote(id, safe='')}"


class SyncTransactionalDomains:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(self, options: MethodOptions | None = None) -> TransactionalDomainList:
        return self._client.request(
            RequestOptions(method="GET", path="/transactional-domains", method_options=options)
        )

    # Calling it again with the same values resumes a setup that stopped part way.
    def create(
        self, params: CreateTransactionalDomainParams, options: MethodOptions | None = None
    ) -> TransactionalDomain:
        return self._client.request(
            RequestOptions(method="POST", path="/transactional-domains", body=params, method_options=options)
        )

    def get(self, id: str, options: MethodOptions | None = None) -> TransactionalDomain:
        return self._client.request(RequestOptions(method="GET", path=_path(id), method_options=options))

    def verify(self, id: str, options: MethodOptions | None = None) -> TransactionalDomain:
        return self._client.request(
            RequestOptions(method="POST", path=f"{_path(id)}/verify", method_options=options)
        )

    def delete(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(RequestOptions(method="DELETE", path=_path(id), method_options=options))


class AsyncTransactionalDomains:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(self, options: MethodOptions | None = None) -> TransactionalDomainList:
        return await self._client.request(
            RequestOptions(method="GET", path="/transactional-domains", method_options=options)
        )

    # Calling it again with the same values resumes a setup that stopped part way.
    async def create(
        self, params: CreateTransactionalDomainParams, options: MethodOptions | None = None
    ) -> TransactionalDomain:
        return await self._client.request(
            RequestOptions(method="POST", path="/transactional-domains", body=params, method_options=options)
        )

    async def get(self, id: str, options: MethodOptions | None = None) -> TransactionalDomain:
        return await self._client.request(RequestOptions(method="GET", path=_path(id), method_options=options))

    async def verify(self, id: str, options: MethodOptions | None = None) -> TransactionalDomain:
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_path(id)}/verify", method_options=options)
        )

    async def delete(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(RequestOptions(method="DELETE", path=_path(id), method_options=options))
