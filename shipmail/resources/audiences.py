from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions
from .._pagination import AsyncPage, SyncPage

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.audience import (
        AddSubscriberParams,
        AddSubscribersBatchParams,
        AddSubscribersBatchResult,
        Audience,
        AudienceFeed,
        CreateAudienceParams,
        ListAudiencesParams,
        ListSubscribersParams,
        ResubscribeSubscriberParams,
        Subscriber,
        SubscriberResult,
        UpdateAudienceParams,
        UpdateAudienceFeedParams,
        UpdateSubscriberParams,
    )
    from .._types.common import MethodOptions, PaginatedResponse
    from .._types.welcome_sequence import (
        CreateWelcomeStepParams,
        DeletedWelcomeStep,
        UpdateWelcomeSequenceParams,
        UpdateWelcomeStepParams,
        WelcomeSequence,
        WelcomeStep,
    )


def _subs(audience_id: str) -> str:
    return f"/audiences/{quote(audience_id, safe='')}/subscribers"


def _feed(audience_id: str) -> str:
    return f"/audiences/{quote(audience_id, safe='')}/feed"


def _welcome(audience_id: str) -> str:
    return f"/audiences/{quote(audience_id, safe='')}/welcome-sequence"


def _welcome_step(audience_id: str, step_id: str) -> str:
    return f"{_welcome(audience_id)}/steps/{quote(step_id, safe='')}"


def _member(audience_id: str, subscriber_id: str) -> str:
    return f"{_subs(audience_id)}/{quote(subscriber_id, safe='')}"


class SyncSubscribers:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def add(
        self, audience_id: str, params: AddSubscriberParams, options: MethodOptions | None = None
    ) -> SubscriberResult:
        return self._client.request(
            RequestOptions(method="POST", path=_subs(audience_id), body=params, method_options=options)
        )

    def add_batch(
        self, audience_id: str, params: AddSubscribersBatchParams, options: MethodOptions | None = None
    ) -> AddSubscribersBatchResult:
        return self._client.request(
            RequestOptions(method="POST", path=f"{_subs(audience_id)}/batch", body=params, method_options=options)
        )

    def list(
        self, audience_id: str, params: ListSubscribersParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path=_subs(audience_id),
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                    "status": params.get("status") if params else None,
                    "email": params.get("email") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(
        self, audience_id: str, *, limit: int | None = None, status: str | None = None, email: str | None = None
    ) -> SyncPage[Subscriber]:
        return SyncPage(self._client, _subs(audience_id), {"limit": limit, "status": status, "email": email})

    def get(self, audience_id: str, subscriber_id: str, options: MethodOptions | None = None) -> Subscriber:
        return self._client.request(
            RequestOptions(method="GET", path=_member(audience_id, subscriber_id), method_options=options)
        )

    def get_by_email(self, audience_id: str, email: str, options: MethodOptions | None = None) -> Subscriber:
        return self._client.request(
            RequestOptions(
                method="GET", path=f"{_subs(audience_id)}/by-email/{quote(email, safe='')}", method_options=options
            )
        )

    def update(
        self, audience_id: str, subscriber_id: str, params: UpdateSubscriberParams, options: MethodOptions | None = None
    ) -> Subscriber:
        return self._client.request(
            RequestOptions(
                method="PATCH", path=_member(audience_id, subscriber_id), body=params, method_options=options
            )
        )

    def unsubscribe(self, audience_id: str, subscriber_id: str, options: MethodOptions | None = None) -> Subscriber:
        return self._client.request(
            RequestOptions(
                method="POST", path=f"{_member(audience_id, subscriber_id)}/unsubscribe", method_options=options
            )
        )

    def resubscribe(
        self,
        audience_id: str,
        subscriber_id: str,
        params: ResubscribeSubscriberParams,
        options: MethodOptions | None = None,
    ) -> Subscriber:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"{_member(audience_id, subscriber_id)}/resubscribe",
                body=params,
                method_options=options,
            )
        )

    def remove(self, audience_id: str, subscriber_id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(method="DELETE", path=_member(audience_id, subscriber_id), method_options=options)
        )


class SyncAudienceFeeds:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def get(self, audience_id: str, options: MethodOptions | None = None) -> AudienceFeed:
        return self._client.request(
            RequestOptions(method="GET", path=_feed(audience_id), method_options=options)
        )

    def update(
        self,
        audience_id: str,
        params: UpdateAudienceFeedParams,
        options: MethodOptions | None = None,
    ) -> AudienceFeed:
        return self._client.request(
            RequestOptions(
                method="PATCH",
                path=_feed(audience_id),
                body=params,
                method_options=options,
            )
        )

    def rotate(self, audience_id: str, options: MethodOptions | None = None) -> AudienceFeed:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"{_feed(audience_id)}/rotate",
                method_options=options,
            )
        )

    def revoke(self, audience_id: str, options: MethodOptions | None = None) -> AudienceFeed:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"{_feed(audience_id)}/revoke",
                method_options=options,
            )
        )


class SyncWelcomeSequences:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def get(self, audience_id: str, options: MethodOptions | None = None) -> WelcomeSequence:
        return self._client.request(
            RequestOptions(method="GET", path=_welcome(audience_id), method_options=options)
        )

    def update(
        self,
        audience_id: str,
        params: UpdateWelcomeSequenceParams,
        options: MethodOptions | None = None,
    ) -> WelcomeSequence:
        return self._client.request(
            RequestOptions(method="PATCH", path=_welcome(audience_id), body=params, method_options=options)
        )

    def create_step(
        self,
        audience_id: str,
        params: CreateWelcomeStepParams,
        options: MethodOptions | None = None,
    ) -> WelcomeStep:
        return self._client.request(
            RequestOptions(
                method="POST",
                path=f"{_welcome(audience_id)}/steps",
                body=params,
                method_options=options,
            )
        )

    def update_step(
        self,
        audience_id: str,
        step_id: str,
        params: UpdateWelcomeStepParams,
        options: MethodOptions | None = None,
    ) -> WelcomeStep:
        return self._client.request(
            RequestOptions(
                method="PATCH",
                path=_welcome_step(audience_id, step_id),
                body=params,
                method_options=options,
            )
        )

    def delete_step(
        self, audience_id: str, step_id: str, options: MethodOptions | None = None
    ) -> DeletedWelcomeStep:
        return self._client.request(
            RequestOptions(method="DELETE", path=_welcome_step(audience_id, step_id), method_options=options)
        )


class SyncAudiences:
    feeds: SyncAudienceFeeds
    subscribers: SyncSubscribers
    welcome_sequence: SyncWelcomeSequences

    def __init__(self, client: Shipmail) -> None:
        self._client = client
        self.feeds = SyncAudienceFeeds(client)
        self.subscribers = SyncSubscribers(client)
        self.welcome_sequence = SyncWelcomeSequences(client)

    def create(self, params: CreateAudienceParams, options: MethodOptions | None = None) -> Audience:
        return self._client.request(
            RequestOptions(method="POST", path="/audiences", body=params, method_options=options)
        )

    def list(
        self, params: ListAudiencesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return self._client.request(
            RequestOptions(
                method="GET",
                path="/audiences",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> SyncPage[Audience]:
        return SyncPage(self._client, "/audiences", {"limit": limit})

    def get(self, id: str, options: MethodOptions | None = None) -> Audience:
        return self._client.request(
            RequestOptions(method="GET", path=f"/audiences/{quote(id, safe='')}", method_options=options)
        )

    def update(self, id: str, params: UpdateAudienceParams, options: MethodOptions | None = None) -> Audience:
        return self._client.request(
            RequestOptions(method="PATCH", path=f"/audiences/{quote(id, safe='')}", body=params, method_options=options)
        )

    def delete(self, id: str, options: MethodOptions | None = None) -> None:
        self._client.request(
            RequestOptions(method="DELETE", path=f"/audiences/{quote(id, safe='')}", method_options=options)
        )


class AsyncSubscribers:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def add(
        self, audience_id: str, params: AddSubscriberParams, options: MethodOptions | None = None
    ) -> SubscriberResult:
        return await self._client.request(
            RequestOptions(method="POST", path=_subs(audience_id), body=params, method_options=options)
        )

    async def add_batch(
        self, audience_id: str, params: AddSubscribersBatchParams, options: MethodOptions | None = None
    ) -> AddSubscribersBatchResult:
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_subs(audience_id)}/batch", body=params, method_options=options)
        )

    async def list(
        self, audience_id: str, params: ListSubscribersParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path=_subs(audience_id),
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                    "status": params.get("status") if params else None,
                    "email": params.get("email") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(
        self, audience_id: str, *, limit: int | None = None, status: str | None = None, email: str | None = None
    ) -> AsyncPage[Subscriber]:
        return AsyncPage(self._client, _subs(audience_id), {"limit": limit, "status": status, "email": email})

    async def get(self, audience_id: str, subscriber_id: str, options: MethodOptions | None = None) -> Subscriber:
        return await self._client.request(
            RequestOptions(method="GET", path=_member(audience_id, subscriber_id), method_options=options)
        )

    async def get_by_email(self, audience_id: str, email: str, options: MethodOptions | None = None) -> Subscriber:
        return await self._client.request(
            RequestOptions(
                method="GET", path=f"{_subs(audience_id)}/by-email/{quote(email, safe='')}", method_options=options
            )
        )

    async def update(
        self, audience_id: str, subscriber_id: str, params: UpdateSubscriberParams, options: MethodOptions | None = None
    ) -> Subscriber:
        return await self._client.request(
            RequestOptions(
                method="PATCH", path=_member(audience_id, subscriber_id), body=params, method_options=options
            )
        )

    async def unsubscribe(
        self, audience_id: str, subscriber_id: str, options: MethodOptions | None = None
    ) -> Subscriber:
        return await self._client.request(
            RequestOptions(
                method="POST", path=f"{_member(audience_id, subscriber_id)}/unsubscribe", method_options=options
            )
        )

    async def resubscribe(
        self,
        audience_id: str,
        subscriber_id: str,
        params: ResubscribeSubscriberParams,
        options: MethodOptions | None = None,
    ) -> Subscriber:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"{_member(audience_id, subscriber_id)}/resubscribe",
                body=params,
                method_options=options,
            )
        )

    async def remove(self, audience_id: str, subscriber_id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(method="DELETE", path=_member(audience_id, subscriber_id), method_options=options)
        )


class AsyncAudienceFeeds:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def get(self, audience_id: str, options: MethodOptions | None = None) -> AudienceFeed:
        return await self._client.request(
            RequestOptions(method="GET", path=_feed(audience_id), method_options=options)
        )

    async def update(
        self,
        audience_id: str,
        params: UpdateAudienceFeedParams,
        options: MethodOptions | None = None,
    ) -> AudienceFeed:
        return await self._client.request(
            RequestOptions(
                method="PATCH",
                path=_feed(audience_id),
                body=params,
                method_options=options,
            )
        )

    async def rotate(self, audience_id: str, options: MethodOptions | None = None) -> AudienceFeed:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"{_feed(audience_id)}/rotate",
                method_options=options,
            )
        )

    async def revoke(self, audience_id: str, options: MethodOptions | None = None) -> AudienceFeed:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"{_feed(audience_id)}/revoke",
                method_options=options,
            )
        )


class AsyncWelcomeSequences:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def get(self, audience_id: str, options: MethodOptions | None = None) -> WelcomeSequence:
        return await self._client.request(
            RequestOptions(method="GET", path=_welcome(audience_id), method_options=options)
        )

    async def update(
        self,
        audience_id: str,
        params: UpdateWelcomeSequenceParams,
        options: MethodOptions | None = None,
    ) -> WelcomeSequence:
        return await self._client.request(
            RequestOptions(method="PATCH", path=_welcome(audience_id), body=params, method_options=options)
        )

    async def create_step(
        self,
        audience_id: str,
        params: CreateWelcomeStepParams,
        options: MethodOptions | None = None,
    ) -> WelcomeStep:
        return await self._client.request(
            RequestOptions(
                method="POST",
                path=f"{_welcome(audience_id)}/steps",
                body=params,
                method_options=options,
            )
        )

    async def update_step(
        self,
        audience_id: str,
        step_id: str,
        params: UpdateWelcomeStepParams,
        options: MethodOptions | None = None,
    ) -> WelcomeStep:
        return await self._client.request(
            RequestOptions(
                method="PATCH",
                path=_welcome_step(audience_id, step_id),
                body=params,
                method_options=options,
            )
        )

    async def delete_step(
        self, audience_id: str, step_id: str, options: MethodOptions | None = None
    ) -> DeletedWelcomeStep:
        return await self._client.request(
            RequestOptions(method="DELETE", path=_welcome_step(audience_id, step_id), method_options=options)
        )


class AsyncAudiences:
    feeds: AsyncAudienceFeeds
    subscribers: AsyncSubscribers
    welcome_sequence: AsyncWelcomeSequences

    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client
        self.feeds = AsyncAudienceFeeds(client)
        self.subscribers = AsyncSubscribers(client)
        self.welcome_sequence = AsyncWelcomeSequences(client)

    async def create(self, params: CreateAudienceParams, options: MethodOptions | None = None) -> Audience:
        return await self._client.request(
            RequestOptions(method="POST", path="/audiences", body=params, method_options=options)
        )

    async def list(
        self, params: ListAudiencesParams | None = None, options: MethodOptions | None = None
    ) -> PaginatedResponse:
        return await self._client.request(
            RequestOptions(
                method="GET",
                path="/audiences",
                query={
                    "cursor": params.get("cursor") if params else None,
                    "limit": params.get("limit") if params else None,
                },
                method_options=options,
            )
        )

    def list_auto_paginating(self, *, limit: int | None = None) -> AsyncPage[Audience]:
        return AsyncPage(self._client, "/audiences", {"limit": limit})

    async def get(self, id: str, options: MethodOptions | None = None) -> Audience:
        return await self._client.request(
            RequestOptions(method="GET", path=f"/audiences/{quote(id, safe='')}", method_options=options)
        )

    async def update(self, id: str, params: UpdateAudienceParams, options: MethodOptions | None = None) -> Audience:
        return await self._client.request(
            RequestOptions(method="PATCH", path=f"/audiences/{quote(id, safe='')}", body=params, method_options=options)
        )

    async def delete(self, id: str, options: MethodOptions | None = None) -> None:
        await self._client.request(
            RequestOptions(method="DELETE", path=f"/audiences/{quote(id, safe='')}", method_options=options)
        )
