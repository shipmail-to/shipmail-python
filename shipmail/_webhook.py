from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

from ._errors import WebhookVerificationError

DEFAULT_TOLERANCE_SECONDS = 300


def _get_header(headers: dict[str, str], name: str) -> str | None:
    lower_name = name.lower()
    for k, v in headers.items():
        if k.lower() == lower_name:
            return v
    return None


def verify_webhook(
    body: str,
    headers: dict[str, str],
    secret: str,
    *,
    tolerance_in_seconds: int = DEFAULT_TOLERANCE_SECONDS,
) -> dict[str, Any]:
    signature = _get_header(headers, "x-shipmail-signature")
    timestamp_str = _get_header(headers, "x-shipmail-timestamp")

    if not signature:
        raise WebhookVerificationError("Missing X-Shipmail-Signature header")
    if not timestamp_str:
        raise WebhookVerificationError("Missing X-Shipmail-Timestamp header")

    try:
        timestamp = int(timestamp_str)
    except ValueError:
        raise WebhookVerificationError("Invalid X-Shipmail-Timestamp header") from None

    now = int(time.time())
    if abs(now - timestamp) > tolerance_in_seconds:
        raise WebhookVerificationError("Webhook timestamp is outside tolerance window")

    payload = f"v1={timestamp}\n{body}"
    expected = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature.encode("utf-8"), expected.encode("ascii")):
        raise WebhookVerificationError("Webhook signature verification failed")

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        raise WebhookVerificationError("Invalid webhook payload: not valid JSON") from None

    return parsed
