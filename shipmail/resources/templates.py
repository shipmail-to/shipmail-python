from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.template import (
        CreateTemplateParams,
        ListTemplatesParams,
        ListTemplateVersionsParams,
        RenderedTemplate,
        RenderTemplateParams,
        Template,
        TemplateVersion,
        UpdateTemplateParams,
    )


class SyncTemplates:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(
        self, params: ListTemplatesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/templates",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[Template]:
        return SyncPage(self._client, "/templates", {"limit": limit})

    def create(self, params: CreateTemplateParams, options: MethodOptions | None = None) -> Template:
        return self._client.request(
            RequestOptions(method="POST", path="/templates", body=params, method_options=options)
        )

    def get(self, id: str, options: MethodOptions | None = None) -> Template:
        return self._client.request(
            RequestOptions(method="GET", path=f"/templates/{quote(id, safe='')}", method_options=options)
        )

    def update(self, id: str, params: UpdateTemplateParams, options: MethodOptions | None = None) -> Template:
        return self._client.request(
            RequestOptions(method="PATCH", path=f"/templates/{quote(id, safe='')}", body=params, method_options=options)
        )

    def delete(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(method="DELETE", path=f"/templates/{quote(id, safe='')}", method_options=options)
        )

    def publish(self, id: str, options: MethodOptions | None = None) -> Template:
        return self._client.request(
            RequestOptions(method="POST", path=f"/templates/{quote(id, safe='')}/publish", method_options=options)
        )

    def render(
        self, id: str, params: RenderTemplateParams | None = None, options: MethodOptions | None = None
    ) -> RenderedTemplate:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/templates/{quote(id, safe='')}/render",
                body=params or {},
                method_options=options,
            )
        )

    def list_versions(
        self, id: str, params: ListTemplateVersionsParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=f"/templates/{quote(id, safe='')}/versions",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_versions_auto_paginating(self, id: str, *, limit: int | None = None) -> SyncPage[TemplateVersion]:
        return SyncPage(self._client, f"/templates/{quote(id, safe='')}/versions", {"limit": limit})

    def get_version(self, id: str, version: int, options: MethodOptions | None = None) -> TemplateVersion:
        return self._client.request(
            RequestOptions(
                method="GET", path=f"/templates/{quote(id, safe='')}/versions/{int(version)}", method_options=options
            )
        )

    def restore_version(self, id: str, version: int, options: MethodOptions | None = None) -> Template:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/templates/{quote(id, safe='')}/versions/{int(version)}/restore",
                method_options=options,
            )
        )


class AsyncTemplates:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(
        self, params: ListTemplatesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/templates",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[Template]:
        return AsyncPage(self._client, "/templates", {"limit": limit})

    async def create(self, params: CreateTemplateParams, options: MethodOptions | None = None) -> Template:
        return await self._client.request(
            RequestOptions(method="POST", path="/templates", body=params, method_options=options)
        )

    async def get(self, id: str, options: MethodOptions | None = None) -> Template:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/templates/{quote(id, safe='')}", method_options=options)
        )

    async def update(self, id: str, params: UpdateTemplateParams, options: MethodOptions | None = None) -> Template:
        return await self._client.request(
            RequestOptions(method="PATCH", path=f"/templates/{quote(id, safe='')}", body=params, method_options=options)
        )

    async def delete(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(method="DELETE", path=f"/templates/{quote(id, safe='')}", method_options=options)
        )

    async def publish(self, id: str, options: MethodOptions | None = None) -> Template:
        return await self._client.request(
            RequestOptions(method="POST", path=f"/templates/{quote(id, safe='')}/publish", method_options=options)
        )

    async def render(
        self, id: str, params: RenderTemplateParams | None = None, options: MethodOptions | None = None
    ) -> RenderedTemplate:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/templates/{quote(id, safe='')}/render",
                body=params or {},
                method_options=options,
            )
        )

    async def list_versions(
        self, id: str, params: ListTemplateVersionsParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=f"/templates/{quote(id, safe='')}/versions",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_versions_auto_paginating(self, id: str, *, limit: int | None = None) -> AsyncPage[TemplateVersion]:
        return AsyncPage(self._client, f"/templates/{quote(id, safe='')}/versions", {"limit": limit})

    async def get_version(self, id: str, version: int, options: MethodOptions | None = None) -> TemplateVersion:
        return await self._client.request(
            RequestOptions(
                method="GET", path=f"/templates/{quote(id, safe='')}/versions/{int(version)}", method_options=options
            )
        )

    async def restore_version(self, id: str, version: int, options: MethodOptions | None = None) -> Template:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/templates/{quote(id, safe='')}/versions/{int(version)}/restore",
                method_options=options,
            )
        )
