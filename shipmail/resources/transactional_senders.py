from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions
    from .._types.transactional import (
        CreateTransactionalSenderParams,
        ListTransactionalSendersParams,
        TransactionalSender,
        TransactionalSenderList,
        UpdateTransactionalSenderParams,
    )


def _path(id: str) -> str:
    return f"/transactional-senders/{quote(id, safe='')}"


class SyncTransactionalSenders:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(
        self, params: ListTransactionalSendersParams | None = None, options: MethodOptions | None = None
    ) -> TransactionalSenderList:
        return self._client.request(RequestOptions(
            method="GET",
            path="/transactional-senders",
            query={"domain_id": params.get("domain_id") if params else None},
            method_options=options,
        ))

    def create(
        self, params: CreateTransactionalSenderParams, options: MethodOptions | None = None
    ) -> TransactionalSender:
        return self._client.request(
            RequestOptions(method="POST", path="/transactional-senders", body=params, method_options=options)
        )

    def get(self, id: str, options: MethodOptions | None = None) -> TransactionalSender:
        return self._client.request(RequestOptions(method="GET", path=_path(id), method_options=options))

    # Turn a sender off with {"state": "disabled"}. There is no delete.
    def update(
        self, id: str, params: UpdateTransactionalSenderParams, options: MethodOptions | None = None
    ) -> TransactionalSender:
        return self._client.request(
            RequestOptions(method="PATCH", path=_path(id), body=params, method_options=options)
        )


class AsyncTransactionalSenders:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(
        self, params: ListTransactionalSendersParams | None = None, options: MethodOptions | None = None
    ) -> TransactionalSenderList:
        return await self._client.request(RequestOptions(
            method="GET",
            path="/transactional-senders",
            query={"domain_id": params.get("domain_id") if params else None},
            method_options=options,
        ))

    async def create(
        self, params: CreateTransactionalSenderParams, options: MethodOptions | None = None
    ) -> TransactionalSender:
        return await self._client.request(
            RequestOptions(method="POST", path="/transactional-senders", body=params, method_options=options)
        )

    async def get(self, id: str, options: MethodOptions | None = None) -> TransactionalSender:
        return await self._client.request(RequestOptions(method="GET", path=_path(id), method_options=options))

    # Turn a sender off with {"state": "disabled"}. There is no delete.
    async def update(
        self, id: str, params: UpdateTransactionalSenderParams, options: MethodOptions | None = None
    ) -> TransactionalSender:
        return await self._client.request(
            RequestOptions(method="PATCH", path=_path(id), body=params, method_options=options)
        )
