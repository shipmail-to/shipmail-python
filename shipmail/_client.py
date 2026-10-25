from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import httpx

from ._base_client import (
    MAX_RETRY_AFTER,
    BaseClient,
    RequestOptions,
    _calculate_backoff,
    _can_retry,
    _retry_delay,
    _is_api_error_body,
    _is_retryable_status,
)
from ._errors import APIConnectionError, ShipmailError, map_error_from_response
from .resources.audiences import AsyncAudiences, SyncAudiences
from .resources.automations import AsyncAutomations, SyncAutomations
from .resources.booking_link import AsyncBookingLinks, SyncBookingLinks
from .resources.booking_page import AsyncBookingPages, SyncBookingPages
from .resources.calendar import AsyncCalendar, SyncCalendar
from .resources.capabilities import AsyncCapabilities, SyncCapabilities
from .resources.organization import AsyncOrganization, SyncOrganization
from .resources.domains import AsyncDomains, SyncDomains
from .resources.mailboxes import AsyncMailboxes, SyncMailboxes
from .resources.members import AsyncMembers, SyncMembers
from .resources.messages import AsyncMessages, SyncMessages
from .resources.newsletters import AsyncNewsletters, SyncNewsletters
from .resources.reply_scans import AsyncReplyScans, SyncReplyScans
from .resources.scheduled_messages import AsyncScheduledMessages, SyncScheduledMessages
from .resources.status import AsyncStatus, SyncStatus
from .resources.suppressions import AsyncSuppressions, SyncSuppressions
from .resources.threads import AsyncThreads, SyncThreads
from .resources.webhooks import AsyncWebhooks, SyncWebhooks

logger = logging.getLogger("shipmail")


class Shipmail(BaseClient):
    audiences: SyncAudiences
    automations: SyncAutomations
    booking_links: SyncBookingLinks
    booking_pages: SyncBookingPages
    calendar: SyncCalendar
    capabilities: SyncCapabilities
    domains: SyncDomains
    mailboxes: SyncMailboxes
    members: SyncMembers
    messages: SyncMessages
    newsletters: SyncNewsletters
    organization: SyncOrganization
    reply_scans: SyncReplyScans
    scheduled_messages: SyncScheduledMessages
    suppressions: SyncSuppressions
    threads: SyncThreads
    webhooks: SyncWebhooks
    status: SyncStatus

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        max_retries: int | None = None,
        timeout: float | None = None,
        default_headers: dict[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        from ._base_client import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT

        super().__init__(
            api_key,
            base_url=base_url or DEFAULT_BASE_URL,
            max_retries=max_retries if max_retries is not None else DEFAULT_MAX_RETRIES,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
            default_headers=default_headers,
        )
        self._http = httpx.Client(transport=transport) if transport else httpx.Client()
        self.audiences = SyncAudiences(self)
        self.automations = SyncAutomations(self)
        self.booking_links = SyncBookingLinks(self)
        self.booking_pages = SyncBookingPages(self)
        self.calendar = SyncCalendar(self)
        self.capabilities = SyncCapabilities(self)
        self.domains = SyncDomains(self)
        self.mailboxes = SyncMailboxes(self)
        self.members = SyncMembers(self)
        self.messages = SyncMessages(self)
        self.newsletters = SyncNewsletters(self)
        self.organization = SyncOrganization(self)
        self.reply_scans = SyncReplyScans(self)
        self.scheduled_messages = SyncScheduledMessages(self)
        self.suppressions = SyncSuppressions(self)
        self.threads = SyncThreads(self)
        self.webhooks = SyncWebhooks(self)
        self.status = SyncStatus(self)

    def request(self, options: RequestOptions) -> Any:
        url = self._build_url(options.path, options.query)
        headers = self._build_headers(options.method_options)
        effective_timeout = self._get_timeout(options.method_options)
        last_error: ShipmailError | None = None
        can_retry = _can_retry(options, headers)
        retry_after_s: float | None = None

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                delay = _calculate_backoff(attempt - 1, retry_after_s)
                logger.debug("Retry attempt %d for %s %s after %.1fs", attempt, options.method, options.path, delay)
                time.sleep(delay)

            try:
                request_headers = dict(headers)
                content: bytes | None = None
                json_body: Any = None

                if options.raw_body is not None:
                    request_headers["Content-Type"] = options.content_type or "application/octet-stream"
                    content = options.raw_body
                elif options.body is not None:
                    request_headers["Content-Type"] = "application/json"
                    json_body = options.body

                response = self._http.request(
                    options.method,
                    url,
                    headers=request_headers,
                    content=content,
                    json=json_body,
                    timeout=effective_timeout,
                )
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = APIConnectionError(str(exc))
                if can_retry and attempt < self._max_retries:
                    retry_after_s = None
                    continue
                raise last_error from exc

            if response.status_code == 204:
                return None

            if response.is_success:
                return response.json()

            request_id = response.headers.get("x-request-id")

            try:
                error_body = response.json()
            except Exception:
                error_body = None

            if _is_api_error_body(error_body):
                last_error = map_error_from_response(response.status_code, error_body, request_id)
            else:
                last_error = ShipmailError(
                    f"Request failed with status {response.status_code}",
                    status=response.status_code,
                    request_id=request_id,
                    retryable=_is_retryable_status(response.status_code),
                )

            retry_after_s = _retry_delay(response.headers.get("retry-after"), last_error)
            if (
                not can_retry
                or not last_error.retryable
                or attempt >= self._max_retries
                or (retry_after_s is not None and retry_after_s > MAX_RETRY_AFTER)
            ):
                raise last_error

        raise last_error or ShipmailError("Request failed after retries")

    def request_bytes(self, options: RequestOptions) -> bytes:
        url = self._build_url(options.path, options.query)
        headers = self._build_headers(options.method_options, accept="application/octet-stream")
        effective_timeout = self._get_timeout(options.method_options)
        last_error: ShipmailError | None = None
        can_retry = _can_retry(options, headers)
        retry_after_s: float | None = None

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                delay = _calculate_backoff(attempt - 1, retry_after_s)
                logger.debug("Retry attempt %d for %s %s after %.1fs", attempt, options.method, options.path, delay)
                time.sleep(delay)

            try:
                response = self._http.request(
                    options.method,
                    url,
                    headers=headers,
                    timeout=effective_timeout,
                )
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = APIConnectionError(str(exc))
                if can_retry and attempt < self._max_retries:
                    retry_after_s = None
                    continue
                raise last_error from exc

            if response.is_success:
                return response.content

            request_id = response.headers.get("x-request-id")

            try:
                error_body = response.json()
            except Exception:
                error_body = None

            if _is_api_error_body(error_body):
                last_error = map_error_from_response(response.status_code, error_body, request_id)
            else:
                last_error = ShipmailError(
                    f"Request failed with status {response.status_code}",
                    status=response.status_code,
                    request_id=request_id,
                    retryable=_is_retryable_status(response.status_code),
                )

            retry_after_s = _retry_delay(response.headers.get("retry-after"), last_error)
            if (
                not can_retry
                or not last_error.retryable
                or attempt >= self._max_retries
                or (retry_after_s is not None and retry_after_s > MAX_RETRY_AFTER)
            ):
                raise last_error

        raise last_error or ShipmailError("Request failed after retries")

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Shipmail:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncShipmail(BaseClient):
    audiences: AsyncAudiences
    automations: AsyncAutomations
    booking_links: AsyncBookingLinks
    booking_pages: AsyncBookingPages
    calendar: AsyncCalendar
    capabilities: AsyncCapabilities
    domains: AsyncDomains
    mailboxes: AsyncMailboxes
    members: AsyncMembers
    messages: AsyncMessages
    newsletters: AsyncNewsletters
    organization: AsyncOrganization
    reply_scans: AsyncReplyScans
    scheduled_messages: AsyncScheduledMessages
    suppressions: AsyncSuppressions
    threads: AsyncThreads
    webhooks: AsyncWebhooks
    status: AsyncStatus

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        max_retries: int | None = None,
        timeout: float | None = None,
        default_headers: dict[str, str] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        from ._base_client import DEFAULT_BASE_URL, DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT

        super().__init__(
            api_key,
            base_url=base_url or DEFAULT_BASE_URL,
            max_retries=max_retries if max_retries is not None else DEFAULT_MAX_RETRIES,
            timeout=timeout if timeout is not None else DEFAULT_TIMEOUT,
            default_headers=default_headers,
        )
        self._http = httpx.AsyncClient(transport=transport) if transport else httpx.AsyncClient()
        self.audiences = AsyncAudiences(self)
        self.automations = AsyncAutomations(self)
        self.booking_links = AsyncBookingLinks(self)
        self.booking_pages = AsyncBookingPages(self)
        self.calendar = AsyncCalendar(self)
        self.capabilities = AsyncCapabilities(self)
        self.domains = AsyncDomains(self)
        self.mailboxes = AsyncMailboxes(self)
        self.members = AsyncMembers(self)
        self.messages = AsyncMessages(self)
        self.newsletters = AsyncNewsletters(self)
        self.organization = AsyncOrganization(self)
        self.reply_scans = AsyncReplyScans(self)
        self.scheduled_messages = AsyncScheduledMessages(self)
        self.suppressions = AsyncSuppressions(self)
        self.threads = AsyncThreads(self)
        self.webhooks = AsyncWebhooks(self)
        self.status = AsyncStatus(self)

    async def request(self, options: RequestOptions) -> Any:
        url = self._build_url(options.path, options.query)
        headers = self._build_headers(options.method_options)
        effective_timeout = self._get_timeout(options.method_options)
        last_error: ShipmailError | None = None
        can_retry = _can_retry(options, headers)
        retry_after_s: float | None = None

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                delay = _calculate_backoff(attempt - 1, retry_after_s)
                logger.debug("Retry attempt %d for %s %s after %.1fs", attempt, options.method, options.path, delay)
                await asyncio.sleep(delay)

            try:
                request_headers = dict(headers)
                content: bytes | None = None
                json_body: Any = None

                if options.raw_body is not None:
                    request_headers["Content-Type"] = options.content_type or "application/octet-stream"
                    content = options.raw_body
                elif options.body is not None:
                    request_headers["Content-Type"] = "application/json"
                    json_body = options.body

                response = await self._http.request(
                    options.method,
                    url,
                    headers=request_headers,
                    content=content,
                    json=json_body,
                    timeout=effective_timeout,
                )
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = APIConnectionError(str(exc))
                if can_retry and attempt < self._max_retries:
                    retry_after_s = None
                    continue
                raise last_error from exc

            if response.status_code == 204:
                return None

            if response.is_success:
                return response.json()

            request_id = response.headers.get("x-request-id")

            try:
                error_body = response.json()
            except Exception:
                error_body = None

            if _is_api_error_body(error_body):
                last_error = map_error_from_response(response.status_code, error_body, request_id)
            else:
                last_error = ShipmailError(
                    f"Request failed with status {response.status_code}",
                    status=response.status_code,
                    request_id=request_id,
                    retryable=_is_retryable_status(response.status_code),
                )

            retry_after_s = _retry_delay(response.headers.get("retry-after"), last_error)
            if (
                not can_retry
                or not last_error.retryable
                or attempt >= self._max_retries
                or (retry_after_s is not None and retry_after_s > MAX_RETRY_AFTER)
            ):
                raise last_error

        raise last_error or ShipmailError("Request failed after retries")

    async def request_bytes(self, options: RequestOptions) -> bytes:
        url = self._build_url(options.path, options.query)
        headers = self._build_headers(options.method_options, accept="application/octet-stream")
        effective_timeout = self._get_timeout(options.method_options)
        last_error: ShipmailError | None = None
        can_retry = _can_retry(options, headers)
        retry_after_s: float | None = None

        for attempt in range(self._max_retries + 1):
            if attempt > 0:
                delay = _calculate_backoff(attempt - 1, retry_after_s)
                logger.debug("Retry attempt %d for %s %s after %.1fs", attempt, options.method, options.path, delay)
                await asyncio.sleep(delay)

            try:
                response = await self._http.request(
                    options.method,
                    url,
                    headers=headers,
                    timeout=effective_timeout,
                )
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = APIConnectionError(str(exc))
                if can_retry and attempt < self._max_retries:
                    retry_after_s = None
                    continue
                raise last_error from exc

            if response.is_success:
                return response.content

            request_id = response.headers.get("x-request-id")

            try:
                error_body = response.json()
            except Exception:
                error_body = None

            if _is_api_error_body(error_body):
                last_error = map_error_from_response(response.status_code, error_body, request_id)
            else:
                last_error = ShipmailError(
                    f"Request failed with status {response.status_code}",
                    status=response.status_code,
                    request_id=request_id,
                    retryable=_is_retryable_status(response.status_code),
                )

            retry_after_s = _retry_delay(response.headers.get("retry-after"), last_error)
            if (
                not can_retry
                or not last_error.retryable
                or attempt >= self._max_retries
                or (retry_after_s is not None and retry_after_s > MAX_RETRY_AFTER)
            ):
                raise last_error

        raise last_error or ShipmailError("Request failed after retries")

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncShipmail:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
