from __future__ import annotations

from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.customer import (
        CreateCustomerParams,
        Customer,
        CustomerFieldList,
        ListCustomersParams,
        ServiceLevelList,
        UpdateCustomerParams,
        UpsertCustomerParams,
    )

_LIST_KEYS = ("cursor", "limit", "email", "domain", "external_source", "external_id", "q", "tag")


def _list_query(params: ListCustomersParams | None) -> dict[str, Any]:
    return {key: params.get(key) if params else None for key in _LIST_KEYS}


def _customer_path(customer_id: str) -> str:
    return f"/customers/{quote(customer_id, safe='')}"


def _external_path(source: str, external_id: str) -> str:
    # Encoded exactly once: "contact/42" is sent as "contact%2F42".
    return f"/customers/external/{quote(source, safe='')}/{quote(external_id, safe='')}"


class SyncCustomers:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(self, params: CreateCustomerParams, options: MethodOptions | None = None) -> Customer:
        return self._client.request(RequestOptions(method="POST", path="/customers", body=params, method_options=options))

    def get(self, customer_id: str, options: MethodOptions | None = None) -> Customer:
        return self._client.request(RequestOptions(method="GET", path=_customer_path(customer_id), method_options=options))

    def list(self, params: ListCustomersParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return self._client.request(RequestOptions(method="GET", path="/customers", query=_list_query(params), method_options=options))

    def list_auto_paginating(self, params: ListCustomersParams | None = None) -> SyncPage[Customer]:
        query = _list_query(params)
        query.pop("cursor")
        return SyncPage(self._client, "/customers", query)

    def update(self, customer_id: str, params: UpdateCustomerParams, options: MethodOptions | None = None) -> Customer:
        return self._client.request(RequestOptions(method="PATCH", path=_customer_path(customer_id), body=params, method_options=options))

    def remove(self, customer_id: str, options: MethodOptions | None = None) -> None:
        self._client.request(RequestOptions(method="DELETE", path=_customer_path(customer_id), method_options=options))

    def upsert_by_external_id(
        self, source: str, external_id: str, params: UpsertCustomerParams, options: MethodOptions | None = None
    ) -> Customer:
        """Create or update the customer a CRM or billing system knows by source and external_id.

        An address or domain owned by another customer is refused with identifier_conflict.
        """
        return self._client.request(
            RequestOptions(method="PUT", path=_external_path(source, external_id), body=params, method_options=options)
        )

    def list_service_levels(self, options: MethodOptions | None = None) -> ServiceLevelList:
        return self._client.request(RequestOptions(method="GET", path="/service-levels", method_options=options))

    def list_fields(self, options: MethodOptions | None = None) -> CustomerFieldList:
        return self._client.request(RequestOptions(method="GET", path="/customer-fields", method_options=options))


class AsyncCustomers:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(self, params: CreateCustomerParams, options: MethodOptions | None = None) -> Customer:
        return await self._client.request(RequestOptions(method="POST", path="/customers", body=params, method_options=options))

    async def get(self, customer_id: str, options: MethodOptions | None = None) -> Customer:
        return await self._client.request(RequestOptions(method="GET", path=_customer_path(customer_id), method_options=options))

    async def list(self, params: ListCustomersParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(method="GET", path="/customers", query=_list_query(params), method_options=options)
        )

    def list_auto_paginating(self, params: ListCustomersParams | None = None) -> AsyncPage[Customer]:
        query = _list_query(params)
        query.pop("cursor")
        return AsyncPage(self._client, "/customers", query)

    async def update(self, customer_id: str, params: UpdateCustomerParams, options: MethodOptions | None = None) -> Customer:
        return await self._client.request(
            RequestOptions(method="PATCH", path=_customer_path(customer_id), body=params, method_options=options)
        )

    async def remove(self, customer_id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(RequestOptions(method="DELETE", path=_customer_path(customer_id), method_options=options))

    async def upsert_by_external_id(
        self, source: str, external_id: str, params: UpsertCustomerParams, options: MethodOptions | None = None
    ) -> Customer:
        return await self._client.request(
            RequestOptions(method="PUT", path=_external_path(source, external_id), body=params, method_options=options)
        )

    async def list_service_levels(self, options: MethodOptions | None = None) -> ServiceLevelList:
        return await self._client.request(RequestOptions(method="GET", path="/service-levels", method_options=options))

    async def list_fields(self, options: MethodOptions | None = None) -> CustomerFieldList:
        return await self._client.request(RequestOptions(method="GET", path="/customer-fields", method_options=options))
