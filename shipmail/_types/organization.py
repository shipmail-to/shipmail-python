from __future__ import annotations

from typing import Literal, TypedDict


class OrganizationAccessOrganization(TypedDict):
    id: str
    name: str


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
