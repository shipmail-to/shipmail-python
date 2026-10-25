from __future__ import annotations

from typing import TYPE_CHECKING

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.common import MethodOptions
    from .._types.organization import OrganizationAccess


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
