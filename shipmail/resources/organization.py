from __future__ import annotations

from typing import TYPE_CHECKING

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions
    from .._types.organization import (
        OrganizationAccess,
        OrganizationAiSettings,
        OrganizationSettings,
        UpdateOrganizationAiSettingsParams,
        UpdateOrganizationParams,
    )


class SyncOrganization:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def access(self, options: MethodOptions | None = None) -> OrganizationAccess:
        """Whether the organization can create mailboxes now, with its plan, trial and capacity.

        Poll it after the owner pays: access appears once Shipmail has recorded the payment.
        """
        return self._client.request(
            RequestOptions(method="GET", path="/organization/access", method_options=options)
        )

    def get(self, options: MethodOptions | None = None) -> OrganizationSettings:
        """The organization's name and default time zone. Requires ``organization:read``."""
        return self._client.request(
            RequestOptions(method="GET", path="/organization", method_options=options)
        )

    def update(
        self, params: UpdateOrganizationParams, options: MethodOptions | None = None
    ) -> OrganizationSettings:
        """Set or clear the default time zone.

        Requires ``organization:write``, and the person behind the credential must be an Owner or Admin.
        """
        return self._client.request(
            RequestOptions(method="PATCH", path="/organization", body=params, method_options=options)
        )

    def get_ai_settings(self, options: MethodOptions | None = None) -> OrganizationAiSettings:
        """The organization's AI switches and whether each is in effect. Requires ``organization:read``."""
        return self._client.request(
            RequestOptions(method="GET", path="/organization/ai-settings", method_options=options)
        )

    def update_ai_settings(
        self, params: UpdateOrganizationAiSettingsParams, options: MethodOptions | None = None
    ) -> OrganizationAiSettings:
        """Turn AI models on or off. Automatic sending is read-only.

        Requires ``organization:write``, and the person behind the credential must be an Owner or Admin.
        """
        return self._client.request(
            RequestOptions(
                method="PATCH", path="/organization/ai-settings", body=params, method_options=options
            )
        )


class AsyncOrganization:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def access(self, options: MethodOptions | None = None) -> OrganizationAccess:
        """Whether the organization can create mailboxes now, with its plan, trial and capacity.

        Poll it after the owner pays: access appears once Shipmail has recorded the payment.
        """
        return await self._client.request(
            RequestOptions(method="GET", path="/organization/access", method_options=options)
        )

    async def get(self, options: MethodOptions | None = None) -> OrganizationSettings:
        """The organization's name and default time zone. Requires ``organization:read``."""
        return await self._client.request(
            RequestOptions(method="GET", path="/organization", method_options=options)
        )

    async def update(
        self, params: UpdateOrganizationParams, options: MethodOptions | None = None
    ) -> OrganizationSettings:
        """Set or clear the default time zone.

        Requires ``organization:write``, and the person behind the credential must be an Owner or Admin.
        """
        return await self._client.request(
            RequestOptions(method="PATCH", path="/organization", body=params, method_options=options)
        )

    async def get_ai_settings(self, options: MethodOptions | None = None) -> OrganizationAiSettings:
        """The organization's AI switches and whether each is in effect. Requires ``organization:read``."""
        return await self._client.request(
            RequestOptions(method="GET", path="/organization/ai-settings", method_options=options)
        )

    async def update_ai_settings(
        self, params: UpdateOrganizationAiSettingsParams, options: MethodOptions | None = None
    ) -> OrganizationAiSettings:
        """Turn AI models on or off. Automatic sending is read-only.

        Requires ``organization:write``, and the person behind the credential must be an Owner or Admin.
        """
        return await self._client.request(
            RequestOptions(
                method="PATCH", path="/organization/ai-settings", body=params, method_options=options
            )
        )
