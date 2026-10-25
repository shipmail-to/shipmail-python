from __future__ import annotations

from typing import Literal, TypedDict


class CapabilityResourceConstraints(TypedDict):
    mailbox_ids: list[str] | None
    domain_ids: list[str] | None
    audience_ids: list[str] | None
    resource_semantics: Literal["legacy-intersection", "union-v2"]


class CapabilitiesResponse(TypedDict):
    capability_version: str
    scopes: list[str]
    constraints: CapabilityResourceConstraints
    allowed_mcp_tools: list[str]
