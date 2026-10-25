from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx

from shipmail import AsyncShipmail, Shipmail


def make_client(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    max_retries: int = 0,
    timeout: float = 30.0,
) -> Shipmail:
    transport = httpx.MockTransport(handler)
    return Shipmail(
        "sm_live_test_key",
        base_url="https://api.test.com/v1",
        max_retries=max_retries,
        timeout=timeout,
        transport=transport,
    )


def make_async_client(
    handler: Callable[[httpx.Request], httpx.Response],
    *,
    max_retries: int = 0,
    timeout: float = 30.0,
) -> AsyncShipmail:
    transport = httpx.MockTransport(handler)
    return AsyncShipmail(
        "sm_live_test_key",
        base_url="https://api.test.com/v1",
        max_retries=max_retries,
        timeout=timeout,
        transport=transport,
    )


def json_response(data: Any, status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code, json=data)
