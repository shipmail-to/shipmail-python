from __future__ import annotations

import logging
import math
import time
import random
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlencode

from ._version import VERSION

logger = logging.getLogger("shipmail")

DEFAULT_BASE_URL = "https://shipmail.to/api/v1"
DEFAULT_MAX_RETRIES = 2
DEFAULT_TIMEOUT = 30.0


@dataclass
class RequestOptions:
    method: str
    path: str
    body: Any = None
    query: dict[str, str | int | bool | None] | None = None
    raw_body: bytes | None = None
    content_type: str | None = None
    method_options: dict[str, Any] | None = None


def _is_retryable_status(status: int) -> bool:
    return status == 429 or status >= 500


MAX_RETRY_AFTER = 60.0


def _calculate_backoff(attempt: int, retry_after_s: float | None = None) -> float:
    if retry_after_s is not None and math.isfinite(retry_after_s) and retry_after_s >= 0:
        return retry_after_s
    base = min(2**attempt * 0.5, 8.0)
    jitter = random.random() * base * 0.5  # noqa: S311
    return base + jitter


def _parse_retry_after(value: str | None) -> float | None:
    if not value or not value.strip():
        return None
    try:
        seconds = float(value)
        return seconds if math.isfinite(seconds) and seconds >= 0 else None
    except ValueError:
        try:
            return max(0.0, parsedate_to_datetime(value).timestamp() - time.time())
        except (ValueError, TypeError, OverflowError):
            return None


def _retry_delay(value: str | None, error: Any) -> float | None:
    delay = _parse_retry_after(value)
    if delay is not None:
        return delay
    seconds = getattr(error, "retry_after", None)
    if isinstance(seconds, (int, float)) and math.isfinite(seconds) and seconds >= 0:
        return float(seconds)
    return None


def _can_retry(options: RequestOptions, headers: dict[str, str]) -> bool:
    method = options.method.upper()
    return method in {"GET", "HEAD", "OPTIONS"} or (
        method in {"POST", "PATCH", "PUT"} and any(
            key.lower() == "idempotency-key" and bool(value.strip()) for key, value in headers.items()
        )
    )


def _is_api_error_body(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    error = value.get("error")
    if not isinstance(error, dict):
        return False
    return isinstance(error.get("type"), str) and isinstance(error.get("message"), str)


class BaseClient:
    _api_key: str
    _base_url: str
    _max_retries: int
    _timeout: float
    _default_headers: dict[str, str]

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: float = DEFAULT_TIMEOUT,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key must not be empty")
        if isinstance(max_retries, bool) or not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError("max_retries must be a non-negative integer")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._timeout = timeout
        self._default_headers = dict(default_headers) if default_headers else {}

    def _build_url(self, path: str, query: dict[str, str | int | bool | None] | None = None) -> str:
        url = f"{self._base_url}{path}"
        if query:
            filtered = {
                k: (str(v).lower() if isinstance(v, bool) else str(v)) for k, v in query.items() if v is not None
            }
            if filtered:
                url = f"{url}?{urlencode(filtered)}"
        return url

    def _build_headers(
        self,
        method_options: dict[str, Any] | None = None,
        *,
        accept: str = "application/json",
    ) -> dict[str, str]:
        headers: dict[str, str] = {
            **self._default_headers,
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": f"shipmail-python/{VERSION}",
            "Accept": accept,
        }
        if method_options:
            extra = method_options.get("headers")
            if extra:
                headers.update(extra)
            idempotency_key = method_options.get("idempotency_key")
            if idempotency_key:
                headers["Idempotency-Key"] = idempotency_key
        return headers

    def _get_timeout(self, method_options: dict[str, Any] | None = None) -> float:
        if method_options:
            t = method_options.get("timeout")
            if t is not None:
                return t
        return self._timeout

    def __repr__(self) -> str:
        redacted = self._api_key[:8] + "..." if len(self._api_key) > 8 else "***"
        return f"{self.__class__.__name__}(api_key='{redacted}', base_url='{self._base_url}')"
