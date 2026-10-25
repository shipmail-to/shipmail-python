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
