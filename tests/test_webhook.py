from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest

from shipmail import WebhookVerificationError, verify_webhook


TEST_SECRET = "whsec_test_secret_key_12345"

VALID_BODY = json.dumps({
    "event_id": "evt_123",
    "event_type": "message.received",
    "created_at": "2025-01-01T00:00:00Z",
    "data": {"id": "msg_456"},
})


def make_signed_payload(
    secret: str,
    body: str,
    timestamp: int | None = None,
) -> tuple[dict[str, str], int]:
    ts = timestamp or int(time.time())
    payload = f"v1={ts}\n{body}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    headers = {"x-shipmail-signature": sig, "x-shipmail-timestamp": str(ts)}
    return headers, ts


class TestVerifyWebhook:
    def test_valid_signature_succeeds(self) -> None:
        headers, _ = make_signed_payload(TEST_SECRET, VALID_BODY)
        event = verify_webhook(VALID_BODY, headers, TEST_SECRET)
        assert event["event_id"] == "evt_123"
        assert event["event_type"] == "message.received"
        assert event["data"] == {"id": "msg_456"}

    def test_invalid_signature_raises(self) -> None:
        headers, _ = make_signed_payload("wrong_secret", VALID_BODY)
        with pytest.raises(WebhookVerificationError, match="Webhook signature verification failed"):
            verify_webhook(VALID_BODY, headers, TEST_SECRET)

    def test_non_ascii_signature_raises_verification_error(self) -> None:
        headers, _ = make_signed_payload(TEST_SECRET, VALID_BODY)
        headers["x-shipmail-signature"] = "\u00e9" * 64
        with pytest.raises(WebhookVerificationError, match="Webhook signature verification failed"):
            verify_webhook(VALID_BODY, headers, TEST_SECRET)

    def test_tampered_body_raises(self) -> None:
        headers, _ = make_signed_payload(TEST_SECRET, VALID_BODY)
        tampered_body = json.dumps({
            "event_id": "evt_999",
            "event_type": "message.received",
            "created_at": "2025-01-01T00:00:00Z",
            "data": {},
        })
        with pytest.raises(WebhookVerificationError, match="Webhook signature verification failed"):
            verify_webhook(tampered_body, headers, TEST_SECRET)

    def test_expired_timestamp_raises(self) -> None:
        old_timestamp = int(time.time()) - 600
        headers, _ = make_signed_payload(TEST_SECRET, VALID_BODY, old_timestamp)
        with pytest.raises(WebhookVerificationError, match="Webhook timestamp is outside tolerance window"):
            verify_webhook(VALID_BODY, headers, TEST_SECRET)

    def test_future_timestamp_raises(self) -> None:
        future_timestamp = int(time.time()) + 600
        headers, _ = make_signed_payload(TEST_SECRET, VALID_BODY, future_timestamp)
        with pytest.raises(WebhookVerificationError, match="Webhook timestamp is outside tolerance window"):
            verify_webhook(VALID_BODY, headers, TEST_SECRET)

    def test_custom_tolerance_works(self) -> None:
        old_timestamp = int(time.time()) - 500
        headers, _ = make_signed_payload(TEST_SECRET, VALID_BODY, old_timestamp)
        event = verify_webhook(VALID_BODY, headers, TEST_SECRET, tolerance_in_seconds=600)
        assert event["event_id"] == "evt_123"

    def test_missing_signature_header_raises(self) -> None:
        ts = str(int(time.time()))
        with pytest.raises(WebhookVerificationError, match="Missing X-Shipmail-Signature header"):
            verify_webhook(VALID_BODY, {"x-shipmail-timestamp": ts}, TEST_SECRET)

    def test_missing_timestamp_header_raises(self) -> None:
        headers, _ = make_signed_payload(TEST_SECRET, VALID_BODY)
        del headers["x-shipmail-timestamp"]
        with pytest.raises(WebhookVerificationError, match="Missing X-Shipmail-Timestamp header"):
            verify_webhook(VALID_BODY, headers, TEST_SECRET)

    def test_missing_both_headers_raises_for_signature_first(self) -> None:
        with pytest.raises(WebhookVerificationError, match="Missing X-Shipmail-Signature header"):
            verify_webhook(VALID_BODY, {}, TEST_SECRET)

    def test_invalid_timestamp_raises(self) -> None:
        headers, _ = make_signed_payload(TEST_SECRET, VALID_BODY)
        headers["x-shipmail-timestamp"] = "not-a-number"
        with pytest.raises(WebhookVerificationError, match="Invalid X-Shipmail-Timestamp header"):
            verify_webhook(VALID_BODY, headers, TEST_SECRET)

    def test_invalid_json_body_raises(self) -> None:
        invalid_body = "not valid json {{{"
        headers, _ = make_signed_payload(TEST_SECRET, invalid_body)
        with pytest.raises(WebhookVerificationError, match="Invalid webhook payload: not valid JSON"):
            verify_webhook(invalid_body, headers, TEST_SECRET)

    def test_verification_error_is_not_retryable(self) -> None:
        with pytest.raises(WebhookVerificationError) as exc_info:
            verify_webhook(VALID_BODY, {}, TEST_SECRET)
        assert exc_info.value.retryable is False
