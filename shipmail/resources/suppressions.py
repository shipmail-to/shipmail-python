from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.suppression import (
        CreateSuppressionParams,
        ListSuppressionsParams,
        NewsletterOptoutLift,
        ResubscribeNewsletterOptoutParams,
        Suppression,
        SuppressionEntry,
        SuppressionEntryReason,
        SuppressionRemoval,
        SuppressionScope,
    )


class SyncSuppressions:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def create(self, params: CreateSuppressionParams, options: MethodOptions | None = None) -> Suppression:
        return self._client.request(RequestOptions(method="POST", path="/suppressions", body=params, method_options=options))

    def list(self, params: ListSuppressionsParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return self._client.request(RequestOptions(
            method="GET",
            path="/suppressions",
            query={
                "cursor": params.get("cursor") if params else None,
                "limit": params.get("limit") if params else None,
                "scope": params.get("scope") if params else None,
                "reason": params.get("reason") if params else None,
            },
            method_options=options,
        ))

    def list_auto_paginating(
        self,
        *,
        limit: int | None = None,
        scope: SuppressionScope | None = None,
        reason: SuppressionEntryReason | None = None,
    ) -> SyncPage[SuppressionEntry]:
        """Suppressions and newsletter opt-outs, newest first. Tell them apart by "source"."""
        return SyncPage(self._client, "/suppressions", {"limit": limit, "scope": scope, "reason": reason})

    def remove(self, email: str, options: MethodOptions | None = None) -> SuppressionRemoval | None:
        """Remove the address-health suppression. A newsletter opt-out is the reader's consent
        and stays. Returns None when only a suppression was removed, and a SuppressionRemoval when
        the address also has an opt-out, which remains. Raises ConflictError (details code
        "consent_opt_out") when the address has only an opt-out: lift it with resubscribe()."""
        return self._client.request(
            RequestOptions(method="DELETE", path=f"/suppressions/{quote(email, safe='')}", method_options=options)
        )

    def resubscribe(
        self, email: str, params: ResubscribeNewsletterOptoutParams, options: MethodOptions | None = None
    ) -> NewsletterOptoutLift:
        """Lift the organization-wide newsletter opt-out of an address, which may be in no
        audience, with fresh consent. Audience statuses do not change: resubscribe an unsubscribed
        subscriber in their audience. Raises ConflictError while a suppression blocks newsletters
        to the address, and NotFoundError when it has no opt-out."""
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"/newsletter-opt-outs/{quote(email, safe='')}/resubscribe",
                body=params,
                method_options=options,
            )
        )


class AsyncSuppressions:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def create(self, params: CreateSuppressionParams, options: MethodOptions | None = None) -> Suppression:
        return await self._client.request(RequestOptions(method="POST", path="/suppressions", body=params, method_options=options))

    async def list(self, params: ListSuppressionsParams | None = None, options: MethodOptions | None = None) -> PaginatedResponse:
        return await self._client.request(RequestOptions(
            method="GET",
            path="/suppressions",
            query={
                "cursor": params.get("cursor") if params else None,
                "limit": params.get("limit") if params else None,
                "scope": params.get("scope") if params else None,
                "reason": params.get("reason") if params else None,
            },
            method_options=options,
        ))

    def list_auto_paginating(
        self,
        *,
        limit: int | None = None,
        scope: SuppressionScope | None = None,
        reason: SuppressionEntryReason | None = None,
    ) -> AsyncPage[SuppressionEntry]:
        """Suppressions and newsletter opt-outs, newest first. Tell them apart by "source"."""
        return AsyncPage(self._client, "/suppressions", {"limit": limit, "scope": scope, "reason": reason})

    async def remove(self, email: str, options: MethodOptions | None = None) -> SuppressionRemoval | None:
        """Remove the address-health suppression. A newsletter opt-out is the reader's consent
        and stays. Returns None when only a suppression was removed, and a SuppressionRemoval when
        the address also has an opt-out, which remains. Raises ConflictError (details code
        "consent_opt_out") when the address has only an opt-out: lift it with resubscribe()."""
        return await self._client.request(
            RequestOptions(method="DELETE", path=f"/suppressions/{quote(email, safe='')}", method_options=options)
        )

    async def resubscribe(
        self, email: str, params: ResubscribeNewsletterOptoutParams, options: MethodOptions | None = None
    ) -> NewsletterOptoutLift:
        """Lift the organization-wide newsletter opt-out of an address, which may be in no
        audience, with fresh consent. Audience statuses do not change: resubscribe an unsubscribed
        subscriber in their audience. Raises ConflictError while a suppression blocks newsletters
        to the address, and NotFoundError when it has no opt-out."""
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"/newsletter-opt-outs/{quote(email, safe='')}/resubscribe",
                body=params,
                method_options=options,
            )
        )
