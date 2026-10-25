from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from ._client import AsyncShipmail, Shipmail

T = TypeVar("T")


class SyncPage(Generic[T]):
    def __init__(
        self,
        client: Shipmail,
        path: str,
        query: dict[str, Any],
    ) -> None:
        self._client = client
        self._path = path
        self._query = query

    def __iter__(self) -> Iterator[T]:
        from ._base_client import RequestOptions

        cursor: str | None = None

        while True:
            query = dict(self._query)
            if cursor is not None:
                query["cursor"] = cursor
            response = self._client.request(
                RequestOptions(
                    method="GET",
                    path=self._path,
                    query=query,
                )
            )

            for item in response["data"]:
                yield item

            pagination = response["pagination"]
            cursor = pagination.get("next_cursor")
            if not pagination.get("has_more"):
                break


class AsyncPage(Generic[T]):
    def __init__(
        self,
        client: AsyncShipmail,
        path: str,
        query: dict[str, Any],
    ) -> None:
        self._client = client
        self._path = path
        self._query = query

    async def __aiter__(self) -> AsyncIterator[T]:
        from ._base_client import RequestOptions

        cursor: str | None = None

        while True:
            query = dict(self._query)
            if cursor is not None:
                query["cursor"] = cursor
            response = await self._client.request(
                RequestOptions(
                    method="GET",
                    path=self._path,
                    query=query,
                )
            )

            for item in response["data"]:
                yield item

            pagination = response["pagination"]
            cursor = pagination.get("next_cursor")
            if not pagination.get("has_more"):
                break
