from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._types.common import ApiErrorBody, ApiErrorDetail, ErrorLimit, ErrorType


# The reason values this SDK knows. A newer server may send others; they pass through.
ERROR_RECOVERY_REASONS = (
    "owner_confirmation_required",
    "subscription_required",
    "trial_capacity",
    "purchased_capacity",
)


class ShipmailError(Exception):
    status: int | None
    type: ErrorType | None
    request_id: str | None
    retryable: bool
    # Why an organization owner must act, when they can lift this refusal in
    # Shipmail. The error's type and status stay what they were.
    reason: str | None
    # The Shipmail page to send the owner to. Retry with a new idempotency key
    # afterwards.
    action_url: str | None
    # The plan, trial or fixed limit that refused the request, when one did.
    limit: ErrorLimit | None

    def __init__(
        self,
        message: str,
        *,
        status: int | None = None,
        type: ErrorType | None = None,
        request_id: str | None = None,
        retryable: bool = False,
        reason: str | None = None,
        action_url: str | None = None,
        limit: ErrorLimit | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.type = type
        self.request_id = request_id
        self.retryable = retryable
        self.reason = reason
        self.action_url = action_url
        self.limit = limit


class AuthenticationError(ShipmailError):
    def __init__(self, message: str, request_id: str | None = None) -> None:
        super().__init__(
            message,
            status=401,
            type="authentication_error",
            request_id=request_id,
            retryable=False,
        )


class AuthorizationError(ShipmailError):
    def __init__(
        self,
        message: str,
        request_id: str | None = None,
        *,
        reason: str | None = None,
        action_url: str | None = None,
    ) -> None:
        super().__init__(
            message,
            status=403,
            type="authorization_error",
            request_id=request_id,
            retryable=False,
            reason=reason,
            action_url=action_url,
        )


class ValidationError(ShipmailError):
    details: list[ApiErrorDetail] | None

    def __init__(
        self,
        message: str,
        *,
        request_id: str | None = None,
        details: list[ApiErrorDetail] | None = None,
        reason: str | None = None,
        action_url: str | None = None,
    ) -> None:
        super().__init__(
            message,
            status=422,
            type="validation_error",
            request_id=request_id,
            retryable=False,
            reason=reason,
            action_url=action_url,
        )
        self.details = details


class QuotaExceededError(ShipmailError):
    def __init__(
        self,
        message: str,
        request_id: str | None = None,
        *,
        reason: str | None = None,
        action_url: str | None = None,
        limit: ErrorLimit | None = None,
    ) -> None:
        super().__init__(
            message,
            status=403,
            type="quota_exceeded",
            request_id=request_id,
            retryable=False,
            reason=reason,
            action_url=action_url,
            limit=limit,
        )


class NotFoundError(ShipmailError):
    def __init__(self, message: str, request_id: str | None = None) -> None:
        super().__init__(
            message,
            status=404,
            type="not_found",
            request_id=request_id,
            retryable=False,
        )


class RateLimitError(ShipmailError):
    retry_after: float | None

    def __init__(
        self,
        message: str,
        *,
        request_id: str | None = None,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(
            message,
            status=429,
            type="rate_limit_error",
            request_id=request_id,
            retryable=True,
        )
        self.retry_after = retry_after


class ConflictError(ShipmailError):
    def __init__(self, message: str, request_id: str | None = None) -> None:
        super().__init__(
            message,
            status=409,
            type="conflict",
            request_id=request_id,
            retryable=False,
        )


class InternalServerError(ShipmailError):
    def __init__(self, message: str, request_id: str | None = None) -> None:
        super().__init__(
            message,
            status=500,
            type="internal_error",
            request_id=request_id,
            retryable=True,
        )


class ReconciliationRequiredError(ShipmailError):
    """A send was interrupted and its outcome is not known.

    Never retried: the message this names may already have gone out, so a retry
    can deliver it twice. ``message_id`` is the tracking message the attempt
    left behind; read it, or quote it in support, before deciding what to send.
    """

    message_id: str | None

    def __init__(
        self,
        message: str,
        request_id: str | None = None,
        *,
        message_id: str | None = None,
    ) -> None:
        super().__init__(
            message,
            status=409,
            type="reconciliation_required",
            request_id=request_id,
            retryable=False,
        )
        self.message_id = message_id


class APIConnectionError(ShipmailError):
    def __init__(self, message: str) -> None:
        super().__init__(message, retryable=True)


class WebhookVerificationError(ShipmailError):
    def __init__(self, message: str) -> None:
        super().__init__(message, retryable=False)


def _read_error_limit(value: Any) -> ErrorLimit | None:
    if not isinstance(value, dict):
        return None
    resource = value.get("resource")
    used = value.get("used")
    limit = value.get("limit")
    scope = value.get("scope")
    if not (
        isinstance(resource, str)
        and isinstance(used, (int, float))
        and not isinstance(used, bool)
        and isinstance(limit, (int, float))
        and not isinstance(limit, bool)
        and isinstance(scope, str)
    ):
        return None
    return {"resource": resource, "used": used, "limit": limit, "scope": scope}


def map_error_from_response(
    status: int,
    body: ApiErrorBody,
    request_id: str | None = None,
) -> ShipmailError:
    error = body["error"]
    rid = request_id or error.get("request_id")

    error_type = error.get("type", "")
    message = error.get("message", "")
    # Only well-formed strings are kept, so an older or unexpected body cannot set them.
    raw_reason = error.get("reason")
    raw_action_url = error.get("action_url")
    reason = raw_reason if isinstance(raw_reason, str) else None
    action_url = raw_action_url if isinstance(raw_action_url, str) else None
    limit = _read_error_limit(error.get("limit"))

    if error_type == "authentication_error":
        return AuthenticationError(message, rid)
    if error_type == "authorization_error":
        return AuthorizationError(message, rid, reason=reason, action_url=action_url)
    if error_type == "quota_exceeded":
        return QuotaExceededError(
            message, rid, reason=reason, action_url=action_url, limit=limit
        )
    if error_type == "validation_error":
        details = error.get("details")
        return ValidationError(
            message,
            request_id=rid,
            details=details,
            reason=reason,
            action_url=action_url,
        )
    if error_type == "not_found":
        return NotFoundError(message, rid)
    if error_type == "rate_limit_error":
        retry_after = error.get("retry_after")
        return RateLimitError(message, request_id=rid, retry_after=retry_after)
    if error_type == "conflict":
        return ConflictError(message, rid)
    if error_type == "reconciliation_required":
        return ReconciliationRequiredError(
            message, rid, message_id=error.get("message_id")
        )
    if error_type == "internal_error":
        return InternalServerError(message, rid)

    return ShipmailError(
        message,
        status=status,
        type=error_type if error_type else None,
        request_id=rid,
        retryable=status >= 500,
        reason=reason,
        action_url=action_url,
        limit=limit,
    )
