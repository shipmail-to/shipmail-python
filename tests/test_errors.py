from __future__ import annotations

from shipmail import (
    ERROR_RECOVERY_REASONS,
    APIConnectionError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ReconciliationRequiredError,
    ShipmailError,
    ValidationError,
    WebhookVerificationError,
)
from shipmail._errors import map_error_from_response


class TestMapErrorFromResponse:
    def test_maps_authentication_error(self) -> None:
        body = {"error": {"type": "authentication_error", "message": "Invalid API key", "request_id": "req_1"}}
        err = map_error_from_response(401, body)
        assert isinstance(err, AuthenticationError)
        assert str(err) == "Invalid API key"
        assert err.status == 401
        assert err.type == "authentication_error"
        assert err.request_id == "req_1"
        assert err.retryable is False

    def test_maps_authorization_error(self) -> None:
        body = {"error": {"type": "authorization_error", "message": "Forbidden", "request_id": "req_2"}}
        err = map_error_from_response(403, body)
        assert isinstance(err, AuthorizationError)
        assert str(err) == "Forbidden"
        assert err.status == 403
        assert err.type == "authorization_error"
        assert err.retryable is False

    def test_maps_validation_error_with_details(self) -> None:
        body = {
            "error": {
                "type": "validation_error",
                "message": "Validation failed",
                "request_id": "req_3",
                "details": [
                    {"field": "name", "message": "Name is required"},
                    {"field": "address", "message": "Invalid email address"},
                    {
                        "field": "preflight.content_policy",
                        "code": "content_policy",
                        "message": "Message contains too many links (21 found, 20 max).",
                    },
                ],
            }
        }
        err = map_error_from_response(422, body)
        assert isinstance(err, ValidationError)
        assert str(err) == "Validation failed"
        assert err.status == 422
        assert err.type == "validation_error"
        assert err.retryable is False
        assert err.details is not None
        assert len(err.details) == 3
        assert err.details[0]["field"] == "name"
        assert err.details[0]["message"] == "Name is required"
        assert err.details[1]["field"] == "address"
        assert err.details[1]["message"] == "Invalid email address"
        assert err.details[2]["field"] == "preflight.content_policy"
        assert err.details[2]["code"] == "content_policy"

    def test_maps_validation_error_without_details(self) -> None:
        body = {"error": {"type": "validation_error", "message": "Invalid input"}}
        err = map_error_from_response(422, body)
        assert isinstance(err, ValidationError)
        assert err.details is None

    def test_maps_not_found(self) -> None:
        body = {"error": {"type": "not_found", "message": "Domain not found", "request_id": "req_4"}}
        err = map_error_from_response(404, body)
        assert isinstance(err, NotFoundError)
        assert str(err) == "Domain not found"
        assert err.status == 404
        assert err.retryable is False

    def test_maps_rate_limit_error_with_retry_after(self) -> None:
        body = {
            "error": {
                "type": "rate_limit_error",
                "message": "Too many requests",
                "request_id": "req_5",
                "retry_after": 30,
            }
        }
        err = map_error_from_response(429, body)
        assert isinstance(err, RateLimitError)
        assert str(err) == "Too many requests"
        assert err.status == 429
        assert err.type == "rate_limit_error"
        assert err.retryable is True
        assert err.retry_after == 30

    def test_maps_rate_limit_error_without_retry_after(self) -> None:
        body = {"error": {"type": "rate_limit_error", "message": "Slow down"}}
        err = map_error_from_response(429, body)
        assert isinstance(err, RateLimitError)
        assert err.retry_after is None

    def test_maps_conflict(self) -> None:
        body = {"error": {"type": "conflict", "message": "Domain already exists", "request_id": "req_6"}}
        err = map_error_from_response(409, body)
        assert isinstance(err, ConflictError)
        assert str(err) == "Domain already exists"
        assert err.status == 409
        assert err.retryable is False

    def test_maps_internal_error(self) -> None:
        body = {"error": {"type": "internal_error", "message": "Something went wrong", "request_id": "req_7"}}
        err = map_error_from_response(500, body)
        assert isinstance(err, InternalServerError)
        assert str(err) == "Something went wrong"
        assert err.status == 500
        assert err.retryable is True

    def test_interrupted_send_is_a_conflict_that_is_never_retried(self) -> None:
        # A retry of an interrupted send can deliver the message twice. This used
        # to arrive as a 500, which the client retries.
        body = {
            "error": {
                "type": "reconciliation_required",
                "message": "The previous send attempt requires reconciliation.",
                "request_id": "req_8",
                "message_id": "msg_interrupted",
            }
        }
        err = map_error_from_response(409, body)
        assert isinstance(err, ReconciliationRequiredError)
        assert err.status == 409
        assert err.retryable is False
        assert err.message_id == "msg_interrupted"

    def test_ordinary_internal_error_carries_no_message_id(self) -> None:
        body = {"error": {"type": "internal_error", "message": "Something went wrong"}}
        err = map_error_from_response(500, body)
        assert isinstance(err, InternalServerError)
        assert err.retryable is True
        assert not hasattr(err, "message_id")

    def test_uses_request_id_parameter_over_body(self) -> None:
        body = {"error": {"type": "not_found", "message": "Not found", "request_id": "req_body"}}
        err = map_error_from_response(404, body, "req_param")
        assert err.request_id == "req_param"

    def test_falls_back_to_body_request_id_when_parameter_is_none(self) -> None:
        body = {"error": {"type": "not_found", "message": "Not found", "request_id": "req_body"}}
        err = map_error_from_response(404, body)
        assert err.request_id == "req_body"

    def test_returns_generic_error_for_unknown_type(self) -> None:
        body = {"error": {"type": "unknown_type", "message": "Unknown error"}}
        err = map_error_from_response(418, body)
        assert isinstance(err, ShipmailError)
        assert not isinstance(err, AuthenticationError)
        assert not isinstance(err, NotFoundError)
        assert str(err) == "Unknown error"
        assert err.status == 418
        assert err.retryable is False

    def test_generic_error_is_retryable_for_5xx(self) -> None:
        body = {"error": {"type": "unknown_type", "message": "Unknown server error"}}
        err = map_error_from_response(503, body)
        assert err.retryable is True


class TestErrorClasses:
    def test_shipmail_error_defaults_retryable_to_false(self) -> None:
        err = ShipmailError("test")
        assert err.retryable is False
        assert err.status is None
        assert err.type is None
        assert err.request_id is None

    def test_connection_error_is_retryable(self) -> None:
        err = APIConnectionError("Connection refused")
        assert err.retryable is True
        assert err.status is None

    def test_webhook_verification_error_is_not_retryable(self) -> None:
        err = WebhookVerificationError("Invalid signature")
        assert err.retryable is False

    def test_all_error_classes_extend_shipmail_error(self) -> None:
        assert isinstance(AuthenticationError("test"), ShipmailError)
        assert isinstance(AuthorizationError("test"), ShipmailError)
        assert isinstance(ValidationError("test"), ShipmailError)
        assert isinstance(NotFoundError("test"), ShipmailError)
        assert isinstance(RateLimitError("test"), ShipmailError)
        assert isinstance(ConflictError("test"), ShipmailError)
        assert isinstance(InternalServerError("test"), ShipmailError)
        assert isinstance(APIConnectionError("test"), ShipmailError)
        assert isinstance(WebhookVerificationError("test"), ShipmailError)
        assert isinstance(QuotaExceededError("test"), ShipmailError)

    def test_all_error_classes_extend_exception(self) -> None:
        assert isinstance(ShipmailError("test"), Exception)
        assert isinstance(AuthenticationError("test"), Exception)
        assert isinstance(APIConnectionError("test"), Exception)
        assert isinstance(WebhookVerificationError("test"), Exception)
        assert isinstance(NotFoundError("test"), Exception)
        assert isinstance(RateLimitError("test"), Exception)
        assert isinstance(InternalServerError("test"), Exception)


class TestOwnerRecoveryFields:
    def test_new_server_fields_reach_existing_classes(self) -> None:
        quota = map_error_from_response(
            403,
            {
                "error": {
                    "type": "quota_exceeded",
                    "message": "Mailbox limit reached (3/3).",
                    "reason": "trial_capacity",
                    "action_url": "https://shipmail.to/billing?org=org_1",
                }
            },
        )
        assert isinstance(quota, QuotaExceededError)
        assert quota.status == 403
        assert quota.reason == "trial_capacity"
        assert quota.action_url == "https://shipmail.to/billing?org=org_1"

        purchase = map_error_from_response(
            403,
            {
                "error": {
                    "type": "authorization_error",
                    "message": "An organization owner must confirm this domain purchase.",
                    "reason": "owner_confirmation_required",
                    "action_url": "https://shipmail.to/domains/review?org=org_1&domain=a.test&years=1",
                }
            },
        )
        assert isinstance(purchase, AuthorizationError)
        assert purchase.reason == "owner_confirmation_required"

        subscription = map_error_from_response(
            422,
            {
                "error": {
                    "type": "validation_error",
                    "message": "A subscription is required to create mailboxes.",
                    "reason": "subscription_required",
                    "action_url": "https://shipmail.to/billing?org=org_1",
                }
            },
        )
        assert isinstance(subscription, ValidationError)
        assert subscription.status == 422
        assert subscription.reason == "subscription_required"

    def test_old_server_body_leaves_fields_empty(self) -> None:
        err = map_error_from_response(
            403, {"error": {"type": "quota_exceeded", "message": "Mailbox limit reached."}}
        )
        assert isinstance(err, QuotaExceededError)
        assert err.reason is None
        assert err.action_url is None
        assert err.limit is None

    def test_unknown_reason_passes_through(self) -> None:
        err = map_error_from_response(
            403,
            {"error": {"type": "quota_exceeded", "message": "Limit.", "reason": "future_reason"}},
        )
        assert err.reason == "future_reason"
        assert "trial_capacity" in ERROR_RECOVERY_REASONS

    def test_limit_refusal_exposes_its_limit(self) -> None:
        err = map_error_from_response(
            403,
            {
                "error": {
                    "type": "quota_exceeded",
                    "message": "Active subscriber limit reached (100).",
                    "reason": "trial_capacity",
                    "action_url": "https://shipmail.to/billing?org=org_1",
                    "limit": {
                        "resource": "audience_subscribers",
                        "used": 100,
                        "limit": 100,
                        "scope": "trial",
                    },
                }
            },
        )
        assert isinstance(err, QuotaExceededError)
        assert err.limit == {
            "resource": "audience_subscribers",
            "used": 100,
            "limit": 100,
            "scope": "trial",
        }

    def test_malformed_limit_is_dropped(self) -> None:
        err = map_error_from_response(
            403,
            {
                "error": {
                    "type": "quota_exceeded",
                    "message": "Limit.",
                    "limit": {"resource": "sends", "used": "many"},  # type: ignore[typeddict-item]
                }
            },
        )
        assert err.limit is None
