from __future__ import annotations

from typing import Literal, TypedDict

from .common import PaginationParams

MemberRole = Literal["owner", "admin", "member"]
MemberMailboxAccessScope = Literal["all", "selected"]


class MemberMailboxAccess(TypedDict):
    scope: MemberMailboxAccessScope
    # Empty for `all`. For `selected`, API-key responses may include only IDs the key can reach.
    mailbox_ids: list[str]


class Member(TypedDict):
    object: Literal["member"]
    id: str
    email: str
    name: str
    role: MemberRole
    mailbox_access: MemberMailboxAccess
    created_at: str


ListMembersParams = PaginationParams

InvitationRole = Literal["admin", "member"]


class Invitation(TypedDict):
    object: Literal["invitation"]
    id: str
    email: str
    role: InvitationRole
    mailbox_access: MemberMailboxAccess
    # Only a `member` can carry `editor`.
    newsletter_role: Literal["editor"] | None
    created_at: str
    expires_at: str | None


class InvitationList(TypedDict):
    data: list[Invitation]


class _InviteMemberParamsRequired(TypedDict):
    email: str
    role: InvitationRole


class InviteMemberParams(_InviteMemberParamsRequired, total=False):
    # Defaults to `selected`. `mailbox_ids` is ignored for `all`.
    mailbox_access: MemberMailboxAccessScope
    mailbox_ids: list[str]
    newsletter_role: Literal["editor"] | None
