from __future__ import annotations

from typing import Literal, TypedDict


class CapabilityResourceConstraints(TypedDict):
    mailbox_ids: list[str] | None
    domain_ids: list[str] | None
    audience_ids: list[str] | None
    resource_semantics: Literal["legacy-intersection", "union-v2"]


class CapabilityOrganizationAi(TypedDict):
    models_enabled: bool
    automatic_send_enabled: bool


class CapabilityOrganization(TypedDict):
    # IANA zone used when a request and the credential's user name none, or None.
    default_timezone: str | None
    # Whether AI models and automatic sending are in effect for the organization now.
    ai: CapabilityOrganizationAi


class CapabilitiesResponse(TypedDict):
    capability_version: str
    scopes: list[str]
    constraints: CapabilityResourceConstraints
    allowed_mcp_tools: list[str]
    organization: CapabilityOrganization
