from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.newsletter import (
        CreateNewsletterFromChangelogParams,
        CreateNewsletterParams,
        ListNewsletterAssetsParams,
        ListNewsletterDomainsParams,
        ListNewsletterSenderIdentitiesParams,
        ListNewslettersParams,
        Newsletter,
        NewsletterAsset,
        NewsletterAssetKind,
        NewsletterAssetListResponse,
        NewsletterAssetUpload,
        NewsletterDomain,
        NewsletterPreflight,
        NewsletterPreview,
        NewsletterSenderIdentity,
        NewsletterTestSend,
        PrepareNewsletterAssetUploadParams,
        RegisterNewsletterAssetFromUrlParams,
        ScheduleNewsletterParams,
        SendNewsletterTestParams,
        SendNewsletterToMoreParams,
        UpdateNewsletterParams,
        UploadNewsletterAssetParams,
    )


def _newsletter(id: str) -> str:
    return f"/newsletters/{quote(id, safe='')}"


class SyncNewsletterDomains:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(
        self, params: ListNewsletterDomainsParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/newsletter-domains",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[NewsletterDomain]:
        return SyncPage(self._client, "/newsletter-domains", {"limit": limit})


class SyncNewsletterSenderIdentities:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(
        self,
        params: ListNewsletterSenderIdentitiesParams | None = None,
        options: MethodOptions | None = None,
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/newsletter-sender-identities",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[NewsletterSenderIdentity]:
        return SyncPage(self._client, "/newsletter-sender-identities", {"limit": limit})


class SyncNewsletterAssets:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(
        self, params: ListNewsletterAssetsParams | None = None, options: MethodOptions | None = None
    ) -> NewsletterAssetListResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/newsletter-assets",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                    "kind": params.get("kind") if params else None,
                    "q": params.get("q") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(
        self,
        *,
        limit: int | None = None,
        kind: NewsletterAssetKind | None = None,
        q: str | None = None,
    ) -> SyncPage[NewsletterAsset]:
        return SyncPage(self._client, "/newsletter-assets", {"limit": limit, "kind": kind, "q": q})

    def upload(self, params: UploadNewsletterAssetParams, options: MethodOptions | None = None) -> NewsletterAsset:
        method_options = dict(options or {})
        headers = dict(method_options.get("headers") or {})
        headers["X-Shipmail-Filename"] = params["filename"]
        method_options["headers"] = headers
        return self._client.request(
            RequestOptions(
                method="POST",
                path="/newsletter-assets",
                raw_body=params["data"],
                content_type=params.get("content_type"),
                method_options=method_options,
            )
        )

    def prepare_upload(
        self, params: PrepareNewsletterAssetUploadParams, options: MethodOptions | None = None
    ) -> NewsletterAssetUpload:
        return self._client.request(
            RequestOptions(
                method="POST",
                path="/newsletter-assets/upload-tokens",
                body=params,
                method_options=options,
            )
        )

    def register_from_url(
        self, params: RegisterNewsletterAssetFromUrlParams, options: MethodOptions | None = None
    ) -> NewsletterAsset:
        return self._client.request(
            RequestOptions(method="POST", path="/newsletter-assets", body=params, method_options=options)
        )


class SyncNewsletters:
    domains: SyncNewsletterDomains
    sender_identities: SyncNewsletterSenderIdentities
    assets: SyncNewsletterAssets

    def __init__(self, client: Shipmail) -> None:
        self._client = client
        self.domains = SyncNewsletterDomains(client)
        self.sender_identities = SyncNewsletterSenderIdentities(client)
        self.assets = SyncNewsletterAssets(client)

    def create(self, params: CreateNewsletterParams, options: MethodOptions | None = None) -> Newsletter:
        return self._client.request(
            RequestOptions(method="POST", path="/newsletters", body=params, method_options=options)
        )

    def create_from_changelog(
        self, params: CreateNewsletterFromChangelogParams, options: MethodOptions | None = None
    ) -> Newsletter:
        return self._client.request(
            RequestOptions(method="POST", path="/newsletters/from-changelog", body=params, method_options=options)
        )

    def list(
        self, params: ListNewslettersParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/newsletters",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[Newsletter]:
        return SyncPage(self._client, "/newsletters", {"limit": limit})

    def get(self, id: str, options: MethodOptions | None = None) -> Newsletter:
        return self._client.request(RequestOptions(method="GET", path=_newsletter(id), method_options=options))

    def update(self, id: str, params: UpdateNewsletterParams, options: MethodOptions | None = None) -> Newsletter:
        return self._client.request(
            RequestOptions(method="PATCH", path=_newsletter(id), body=params, method_options=options)
        )

    def preflight(self, id: str, options: MethodOptions | None = None) -> NewsletterPreflight:
        return self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/preflight", method_options=options)
        )

    def preview(self, id: str, options: MethodOptions | None = None) -> NewsletterPreview:
        return self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/preview", method_options=options)
        )

    def send_test(
        self, id: str, params: SendNewsletterTestParams, options: MethodOptions | None = None
    ) -> NewsletterTestSend:
        return self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/test-send", body=params, method_options=options)
        )

    def schedule(self, id: str, params: ScheduleNewsletterParams, options: MethodOptions | None = None) -> Newsletter:
        return self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/schedule", body=params, method_options=options)
        )

    def cancel(self, id: str, options: MethodOptions | None = None) -> Newsletter:
        return self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/cancel", method_options=options)
        )

    def resume(self, id: str, options: MethodOptions | None = None) -> Newsletter:
        return self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/resume", method_options=options)
        )

    def send_to_more(
        self,
        id: str,
        params: SendNewsletterToMoreParams | None = None,
        options: MethodOptions | None = None,
    ) -> Newsletter:
        """Send a newsletter scheduled with a limit to the next held subscribers, or to all of them."""
        return self._client.request(
            RequestOptions(
                method="POST", path=f"{_newsletter(id)}/send-more", body=params or {}, method_options=options
            )
        )


class AsyncNewsletterDomains:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(
        self, params: ListNewsletterDomainsParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/newsletter-domains",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[NewsletterDomain]:
        return AsyncPage(self._client, "/newsletter-domains", {"limit": limit})


class AsyncNewsletterSenderIdentities:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(
        self,
        params: ListNewsletterSenderIdentitiesParams | None = None,
        options: MethodOptions | None = None,
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/newsletter-sender-identities",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[NewsletterSenderIdentity]:
        return AsyncPage(self._client, "/newsletter-sender-identities", {"limit": limit})


class AsyncNewsletterAssets:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(
        self, params: ListNewsletterAssetsParams | None = None, options: MethodOptions | None = None
    ) -> NewsletterAssetListResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/newsletter-assets",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                    "kind": params.get("kind") if params else None,
                    "q": params.get("q") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(
        self,
        *,
        limit: int | None = None,
        kind: NewsletterAssetKind | None = None,
        q: str | None = None,
    ) -> AsyncPage[NewsletterAsset]:
        return AsyncPage(self._client, "/newsletter-assets", {"limit": limit, "kind": kind, "q": q})

    async def upload(
        self, params: UploadNewsletterAssetParams, options: MethodOptions | None = None
    ) -> NewsletterAsset:
        method_options = dict(options or {})
        headers = dict(method_options.get("headers") or {})
        headers["X-Shipmail-Filename"] = params["filename"]
        method_options["headers"] = headers
        return await self._client.request(
            RequestOptions(
                method="POST",
                path="/newsletter-assets",
                raw_body=params["data"],
                content_type=params.get("content_type"),
                method_options=method_options,
            )
        )

    async def prepare_upload(
        self, params: PrepareNewsletterAssetUploadParams, options: MethodOptions | None = None
    ) -> NewsletterAssetUpload:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path="/newsletter-assets/upload-tokens",
                body=params,
                method_options=options,
            )
        )

    async def register_from_url(
        self, params: RegisterNewsletterAssetFromUrlParams, options: MethodOptions | None = None
    ) -> NewsletterAsset:
        return await self._client.request(
            RequestOptions(method="POST", path="/newsletter-assets", body=params, method_options=options)
        )


class AsyncNewsletters:
    domains: AsyncNewsletterDomains
    sender_identities: AsyncNewsletterSenderIdentities
    assets: AsyncNewsletterAssets

    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client
        self.domains = AsyncNewsletterDomains(client)
        self.sender_identities = AsyncNewsletterSenderIdentities(client)
        self.assets = AsyncNewsletterAssets(client)

    async def create(self, params: CreateNewsletterParams, options: MethodOptions | None = None) -> Newsletter:
        return await self._client.request(
            RequestOptions(method="POST", path="/newsletters", body=params, method_options=options)
        )

    async def create_from_changelog(
        self, params: CreateNewsletterFromChangelogParams, options: MethodOptions | None = None
    ) -> Newsletter:
        return await self._client.request(
            RequestOptions(method="POST", path="/newsletters/from-changelog", body=params, method_options=options)
        )

    async def list(
        self, params: ListNewslettersParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/newsletters",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[Newsletter]:
        return AsyncPage(self._client, "/newsletters", {"limit": limit})

    async def get(self, id: str, options: MethodOptions | None = None) -> Newsletter:
        return await self._client.request(RequestOptions(method="GET", path=_newsletter(id), method_options=options))

    async def update(self, id: str, params: UpdateNewsletterParams, options: MethodOptions | None = None) -> Newsletter:
        return await self._client.request(
            RequestOptions(method="PATCH", path=_newsletter(id), body=params, method_options=options)
        )

    async def preflight(self, id: str, options: MethodOptions | None = None) -> NewsletterPreflight:
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/preflight", method_options=options)
        )

    async def preview(self, id: str, options: MethodOptions | None = None) -> NewsletterPreview:
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/preview", method_options=options)
        )

    async def send_test(
        self, id: str, params: SendNewsletterTestParams, options: MethodOptions | None = None
    ) -> NewsletterTestSend:
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/test-send", body=params, method_options=options)
        )

    async def schedule(
        self, id: str, params: ScheduleNewsletterParams, options: MethodOptions | None = None
    ) -> Newsletter:
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/schedule", body=params, method_options=options)
        )

    async def cancel(self, id: str, options: MethodOptions | None = None) -> Newsletter:
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/cancel", method_options=options)
        )

    async def resume(self, id: str, options: MethodOptions | None = None) -> Newsletter:
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_newsletter(id)}/resume", method_options=options)
        )

    async def send_to_more(
        self,
        id: str,
        params: SendNewsletterToMoreParams | None = None,
        options: MethodOptions | None = None,
    ) -> Newsletter:
        """Send a newsletter scheduled with a limit to the next held subscribers, or to all of them."""
        return await self._client.request(
            RequestOptions(
                method="POST", path=f"{_newsletter(id)}/send-more", body=params or {}, method_options=options
            )
        )
