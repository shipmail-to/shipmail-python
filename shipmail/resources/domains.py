from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.domain import (
        CreateDomainParams,
        Domain,
        DomainDnsRecordSet,
        DomainHealth,
        DomainSearchResponse,
        DomainVerificationResult,
        ListDomainsParams,
        RegisterDomainParams,
        SearchDomainsParams,
        UpdateDomainParams,
    )


class SyncDomains:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(self, params: CreateDomainParams, options: MethodOptions | None = None) -> Domain:
        return self._client.request(RequestOptions(method="POST", path="/domains", body=params, method_options=options))

    def list(self, params: ListDomainsParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return self._client.request(RequestOptions(
            method="GET",
            path="/domains",
            query={"cursor": params.get("cursor") if params else None, "limit": params.get("limit") if params else None},
            method_options=options,
        ))

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[Domain]:
        return SyncPage(self._client, "/domains", {"limit": limit})

    def get(self, id: str, options: MethodOptions | None = None) -> Domain:
        return self._client.request(RequestOptions(method="GET", path=f"/domains/{quote(id, safe='')}", method_options=options))

    def get_dns_records(self, id: str, options: MethodOptions | None = None) -> DomainDnsRecordSet:
        return self._client.request(RequestOptions(method="GET", path=f"/domains/{quote(id, safe='')}/dns-records", method_options=options))

    def get_health(self, id: str, options: MethodOptions | None = None) -> DomainHealth:
        return self._client.request(RequestOptions(method="GET", path=f"/domains/{quote(id, safe='')}/health", method_options=options))

    def update(self, id: str, params: UpdateDomainParams, options: MethodOptions | None = None) -> Domain:
        return self._client.request(RequestOptions(method="PATCH", path=f"/domains/{quote(id, safe='')}", body=params, method_options=options))

    def delete(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(RequestOptions(method="DELETE", path=f"/domains/{quote(id, safe='')}", method_options=options))

    def verify(self, id: str, options: MethodOptions | None = None) -> DomainVerificationResult:
        return self._client.request(RequestOptions(method="POST", path=f"/domains/{quote(id, safe='')}/verification", method_options=options))

    def search(self, params: SearchDomainsParams, options: MethodOptions | None = None) -> DomainSearchResponse:
        return self._client.request(RequestOptions(method="POST", path="/domains/search", body=params, method_options=options))

    def register(self, params: RegisterDomainParams, options: MethodOptions | None = None) -> Domain:
        return self._client.request(RequestOptions(method="POST", path="/domains/register", body=params, method_options=options))


class AsyncDomains:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(self, params: CreateDomainParams, options: MethodOptions | None = None) -> Domain:
        return await self._client.request(RequestOptions(method="POST", path="/domains", body=params, method_options=options))

    async def list(self, params: ListDomainsParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return await self._client.request(RequestOptions(
            method="GET",
            path="/domains",
            query={"cursor": params.get("cursor") if params else None, "limit": params.get("limit") if params else None},
            method_options=options,
        ))

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[Domain]:
        return AsyncPage(self._client, "/domains", {"limit": limit})

    async def get(self, id: str, options: MethodOptions | None = None) -> Domain:
        return await self._client.request(RequestOptions(method="GET", path=f"/domains/{quote(id, safe='')}", method_options=options))

    async def get_dns_records(self, id: str, options: MethodOptions | None = None) -> DomainDnsRecordSet:
        return await self._client.request(RequestOptions(method="GET", path=f"/domains/{quote(id, safe='')}/dns-records", method_options=options))

    async def get_health(self, id: str, options: MethodOptions | None = None) -> DomainHealth:
        return await self._client.request(RequestOptions(method="GET", path=f"/domains/{quote(id, safe='')}/health", method_options=options))

    async def update(self, id: str, params: UpdateDomainParams, options: MethodOptions | None = None) -> Domain:
        return await self._client.request(RequestOptions(method="PATCH", path=f"/domains/{quote(id, safe='')}", body=params, method_options=options))

    async def delete(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(RequestOptions(method="DELETE", path=f"/domains/{quote(id, safe='')}", method_options=options))

    async def verify(self, id: str, options: MethodOptions | None = None) -> DomainVerificationResult:
        return await self._client.request(RequestOptions(method="POST", path=f"/domains/{quote(id, safe='')}/verification", method_options=options))

    async def search(self, params: SearchDomainsParams, options: MethodOptions | None = None) -> DomainSearchResponse:
        return await self._client.request(RequestOptions(method="POST", path="/domains/search", body=params, method_options=options))

    async def register(self, params: RegisterDomainParams, options: MethodOptions | None = None) -> Domain:
        return await self._client.request(RequestOptions(method="POST", path="/domains/register", body=params, method_options=options))
