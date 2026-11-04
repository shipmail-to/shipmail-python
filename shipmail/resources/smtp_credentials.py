from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions, OneTimeSecretMethodOptions
    from .._types.smtp_credential import (
        CreatedSmtpCredential,
        CreateSmtpCredentialParams,
        ListSmtpCredentialsParams,
        SmtpCredentialList,
    )


class SyncSmtpCredentials:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(
        self, params: ListSmtpCredentialsParams | None = None, options: MethodOptions | None = None
    ) -> SmtpCredentialList:
        return self._client.request(RequestOptions(
            method="GET",
            path="/smtp-credentials",
            query={"from": params.get("from") if params else None},
            method_options=options,
        ))

    # The password is in this response only. An Idempotency-Key is refused.
    def create(
        self, params: CreateSmtpCredentialParams, options: OneTimeSecretMethodOptions | None = None
    ) -> CreatedSmtpCredential:
        return self._client.request(
            RequestOptions(method="POST", path="/smtp-credentials", body=params, method_options=options)
        )

    def revoke(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(method="DELETE", path=f"/smtp-credentials/{quote(id, safe='')}", method_options=options)
        )


class AsyncSmtpCredentials:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(
        self, params: ListSmtpCredentialsParams | None = None, options: MethodOptions | None = None
    ) -> SmtpCredentialList:
        return await self._client.request(RequestOptions(
            method="GET",
            path="/smtp-credentials",
            query={"from": params.get("from") if params else None},
            method_options=options,
        ))

    # The password is in this response only. An Idempotency-Key is refused.
    async def create(
        self, params: CreateSmtpCredentialParams, options: OneTimeSecretMethodOptions | None = None
    ) -> CreatedSmtpCredential:
        return await self._client.request(
            RequestOptions(method="POST", path="/smtp-credentials", body=params, method_options=options)
        )

    async def revoke(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(method="DELETE", path=f"/smtp-credentials/{quote(id, safe='')}", method_options=options)
        )
