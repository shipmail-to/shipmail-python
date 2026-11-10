from __future__ import annotations

from typing import Literal, TypedDict


class OrganizationAccessOrganization(TypedDict):
    id: str
    name: str
    # IANA zone used when a request and the credential's user name none.
    default_timezone: str | None


class OrganizationAccessTrial(TypedDict):
    active: bool
    ends_at: str | None
    # No subscription yet and the owner never had a trial. Checkout still confirms it.
    eligible: bool


class OrganizationAccessMailboxes(TypedDict):
    limit: int
    used: int


class OrganizationAccess(TypedDict):
    object: Literal["organization_access"]
    organization: OrganizationAccessOrganization
    plan: Literal["free", "solo", "pro", "team", "scale"]
    # Mailboxes can be created now, by the same rule mailbox creation applies.
    has_access: bool
    trial: OrganizationAccessTrial
    mailboxes: OrganizationAccessMailboxes
    # Newsletter sending is available. It is not during a trial.
    newsletters_allowed: bool


class OrganizationSettings(TypedDict):
    object: Literal["organization"]
    id: str
    name: str
    # IANA zone used by availability and timed event creation when neither the request nor the
    # calendar time zone of the person behind the credential names one. None falls back to Etc/UTC.
    default_timezone: str | None


class UpdateOrganizationParams(TypedDict):
    # An IANA zone such as "Europe/Paris", or None to clear it.
    default_timezone: str | None


class OrganizationAiSettingsEffective(TypedDict):
    models_enabled: bool
    automatic_send_enabled: bool


class OrganizationAiSettings(TypedDict):
    object: Literal["organization_ai_settings"]
    # The organization's own switch for AI features.
    models_enabled: bool
    # Read-only: whether automations may send AI-drafted replies without review.
    automatic_send_enabled: bool
    # Whether each switch is in effect. Shipmail can hold either off for every organization.
    effective: OrganizationAiSettingsEffective


class UpdateOrganizationAiSettingsParams(TypedDict):
    # automatic_send_enabled is read-only and cannot be changed over the API.
    models_enabled: bool
