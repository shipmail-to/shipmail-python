from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse, WebhookDeliveryStatus, WebhookEventType
    from .._types.webhook import (
        CreateWebhookParams,
        ListDeliveriesParams,
        ListWebhooksParams,
        RotateSecretResponse,
        TestWebhookResponse,
        UpdateWebhookParams,
        Webhook,
        WebhookDelivery,
        WebhookDeliveryDetail,
        WebhookWithSecret,
    )


class SyncWebhooks:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(self, params: CreateWebhookParams, options: MethodOptions | None = None) -> WebhookWithSecret:
        return self._client.request(
            RequestOptions(method="POST", path="/webhooks", body=params, method_options=options)
        )

    def list(self, params: ListWebhooksParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/webhooks",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[Webhook]:
        return SyncPage(self._client, "/webhooks", {"limit": limit})

    def get(self, id: str, options: MethodOptions | None = None) -> Webhook:
        return self._client.request(
            RequestOptions(method="GET", path=f"/webhooks/{quote(id, safe='')}", method_options=options)
        )

    def update(self, id: str, params: UpdateWebhookParams, options: MethodOptions | None = None) -> Webhook:
        return self._client.request(
            RequestOptions(method="PATCH", path=f"/webhooks/{quote(id, safe='')}", body=params, method_options=options)
        )

    def delete(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(method="DELETE", path=f"/webhooks/{quote(id, safe='')}", method_options=options)
        )

    def rotate_secret(self, id: str, options: MethodOptions | None = None) -> RotateSecretResponse:
        return self._client.request(
            RequestOptions(method="POST", path=f"/webhooks/{quote(id, safe='')}/rotate-secret", method_options=options)
        )

    def test(self, id: str, options: MethodOptions | None = None) -> TestWebhookResponse:
        return self._client.request(
            RequestOptions(method="POST", path=f"/webhooks/{quote(id, safe='')}/test", method_options=options)
        )

    def list_deliveries(
        self, id: str, params: ListDeliveriesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/webhooks/{quote(id, safe='')}/deliveries",
                query={
                    "status": params.get("status") if params else None,
                    "event_type": params.get("event_type") if params else None,
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_deliveries_auto_paginating(
        self,
        id: str,
        *,
        status: WebhookDeliveryStatus | None = None,
        event_type: WebhookEventType | None = None,
        limit: int | None = None,
    ) -> SyncPage[WebhookDelivery]:
        return SyncPage(
            self._client,
            f"/webhooks/{quote(id, safe='')}/deliveries",
            {"status": status, "event_type": event_type, "limit": limit},
        )

    def get_delivery(
        self,
        id: str,
        delivery_id: str,
        options: MethodOptions | None = None,
    ) -> WebhookDeliveryDetail:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/webhooks/{quote(id, safe='')}/deliveries/{quote(delivery_id, safe='')}",
                method_options=options,
            )
        )

    def replay_delivery(
        self,
        id: str,
        delivery_id: str,
        options: MethodOptions | None = None,
    ) -> WebhookDeliveryDetail:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/webhooks/{quote(id, safe='')}/deliveries/{quote(delivery_id, safe='')}/replay",
                method_options=options,
            )
        )


class AsyncWebhooks:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(self, params: CreateWebhookParams, options: MethodOptions | None = None) -> WebhookWithSecret:
        return await self._client.request(
            RequestOptions(method="POST", path="/webhooks", body=params, method_options=options)
        )

    async def list(
        self, params: ListWebhooksParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/webhooks",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[Webhook]:
        return AsyncPage(self._client, "/webhooks", {"limit": limit})

    async def get(self, id: str, options: MethodOptions | None = None) -> Webhook:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/webhooks/{quote(id, safe='')}", method_options=options)
        )

    async def update(self, id: str, params: UpdateWebhookParams, options: MethodOptions | None = None) -> Webhook:
        return await self._client.request(
            RequestOptions(method="PATCH", path=f"/webhooks/{quote(id, safe='')}", body=params, method_options=options)
        )

    async def delete(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(method="DELETE", path=f"/webhooks/{quote(id, safe='')}", method_options=options)
        )

    async def rotate_secret(self, id: str, options: MethodOptions | None = None) -> RotateSecretResponse:
        return await self._client.request(
            RequestOptions(method="POST", path=f"/webhooks/{quote(id, safe='')}/rotate-secret", method_options=options)
        )

    async def test(self, id: str, options: MethodOptions | None = None) -> TestWebhookResponse:
        return await self._client.request(
            RequestOptions(method="POST", path=f"/webhooks/{quote(id, safe='')}/test", method_options=options)
        )

    async def list_deliveries(
        self, id: str, params: ListDeliveriesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/webhooks/{quote(id, safe='')}/deliveries",
                query={
                    "status": params.get("status") if params else None,
                    "event_type": params.get("event_type") if params else None,
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_deliveries_auto_paginating(
        self,
        id: str,
        *,
        status: WebhookDeliveryStatus | None = None,
        event_type: WebhookEventType | None = None,
        limit: int | None = None,
    ) -> AsyncPage[WebhookDelivery]:
        return AsyncPage(
            self._client,
            f"/webhooks/{quote(id, safe='')}/deliveries",
            {"status": status, "event_type": event_type, "limit": limit},
        )

    async def get_delivery(
        self,
        id: str,
        delivery_id: str,
        options: MethodOptions | None = None,
    ) -> WebhookDeliveryDetail:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/webhooks/{quote(id, safe='')}/deliveries/{quote(delivery_id, safe='')}",
                method_options=options,
            )
        )

    async def replay_delivery(
        self,
        id: str,
        delivery_id: str,
        options: MethodOptions | None = None,
    ) -> WebhookDeliveryDetail:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/webhooks/{quote(id, safe='')}/deliveries/{quote(delivery_id, safe='')}/replay",
                method_options=options,
            )
        )
