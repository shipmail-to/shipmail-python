from __future__ import annotations

import json
from typing import get_args

import httpx
import pytest

from shipmail import MemberRole
from tests.conftest import json_response, make_async_client, make_client

mock_member = {
    "object": "member",
    "id": "mem_alice",
    "email": "alice@acme.com",
    "name": "Alice",
    "role": "admin",
    "mailbox_access": {"scope": "selected", "mailbox_ids": ["mbx_support"]},
    "created_at": "2026-01-01T00:00:00Z",
}


def test_member_role_and_mailbox_access_types_match_public_contract() -> None:
    assert get_args(MemberRole) == ("owner", "admin", "member")
    assert mock_member["mailbox_access"] == {
        "scope": "selected",
        "mailbox_ids": ["mbx_support"],
    }


class TestList:
    def test_sends_get_members_with_pagination(self) -> None:
        response = {"data": [mock_member], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/members"
            assert request.url.params.get("cursor") == "cur_abc"
            assert request.url.params.get("limit") == "50"
            return json_response(response)

        client = make_client(handler)
        result = client.members.list({"cursor": "cur_abc", "limit": 50})
        assert result["data"] == [mock_member]


class TestGet:
    def test_sends_get_member_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/members/mem_alice"
            return json_response(mock_member)

        client = make_client(handler)
        assert client.members.get("mem_alice") == mock_member

    def test_encodes_member_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.raw_path == b"/v1/members/a%2Fb"
            return json_response(mock_member)

        client = make_client(handler)
        client.members.get("a/b")


class TestAsyncMembers:
    @pytest.mark.asyncio
    async def test_lists_members_with_selected_mailbox_access(self) -> None:
        response = {"data": [mock_member], "pagination": {"next_cursor": None, "has_more": False}}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/members"
            assert request.url.params.get("cursor") == "cur_abc"
            assert request.url.params.get("limit") == "50"
            return json_response(response)

        client = make_async_client(handler)
        result = await client.members.list({"cursor": "cur_abc", "limit": 50})
        assert result["data"][0]["mailbox_access"] == {
            "scope": "selected",
            "mailbox_ids": ["mbx_support"],
        }

    @pytest.mark.asyncio
    async def test_gets_member_with_all_mailbox_access(self) -> None:
        owner = {
            **mock_member,
            "id": "mem_owner",
            "role": "owner",
            "mailbox_access": {"scope": "all", "mailbox_ids": []},
        }

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/members/mem_owner"
            return json_response(owner)

        client = make_async_client(handler)
        result = await client.members.get("mem_owner")
        assert result["mailbox_access"] == {"scope": "all", "mailbox_ids": []}


mock_invitation = {
    "object": "invitation",
    "id": "inv_bob",
    "email": "bob@acme.com",
    "role": "member",
    "mailbox_access": {"scope": "selected", "mailbox_ids": ["mbx_support"]},
    "newsletter_role": "editor",
    "created_at": "2026-10-27T00:00:00Z",
    "expires_at": "2026-11-03T00:00:00Z",
}


class TestInvitations:
    def test_lists_invitations(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/members/invitations"
            return json_response({"data": [mock_invitation]})

        client = make_client(handler)
        assert client.members.list_invitations()["data"] == [mock_invitation]

    def test_invites_with_idempotency_key(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/members/invitations"
            assert request.headers["idempotency-key"] == "invite-bob"
            assert json.loads(request.content) == {
                "email": "bob@acme.com",
                "role": "member",
                "mailbox_ids": ["mbx_support"],
                "newsletter_role": "editor",
            }
            return json_response(mock_invitation, status_code=201)

        client = make_client(handler)
        result = client.members.invite(
            {
                "email": "bob@acme.com",
                "role": "member",
                "mailbox_ids": ["mbx_support"],
                "newsletter_role": "editor",
            },
            {"idempotency_key": "invite-bob"},
        )
        assert result == mock_invitation

    def test_cancels_invitation(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.raw_path == b"/v1/members/invitations/inv%2Fbob"
            return httpx.Response(204)

        client = make_client(handler)
        assert client.members.cancel_invitation("inv/bob") is None


class TestMailboxAccess:
    def test_grants_and_revokes_mailbox_access(self) -> None:
        calls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(f"{request.method} {request.url.raw_path.decode()}")
            assert request.content == b""
            return json_response(mock_member)

        client = make_client(handler)
        assert client.members.grant_mailbox_access("mem_alice", "mbx/sales") == mock_member
        assert client.members.revoke_mailbox_access("mem_alice", "mbx/sales") == mock_member
        assert calls == [
            "PUT /v1/members/mem_alice/mailboxes/mbx%2Fsales",
            "DELETE /v1/members/mem_alice/mailboxes/mbx%2Fsales",
        ]


class TestAsyncMemberWrites:
    @pytest.mark.asyncio
    async def test_invites_lists_and_cancels(self) -> None:
        calls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(f"{request.method} {request.url.path}")
            if request.method == "POST":
                assert json.loads(request.content) == {
                    "email": "bob@acme.com",
                    "role": "admin",
                    "mailbox_access": "all",
                }
                return json_response(mock_invitation, status_code=201)
            if request.method == "DELETE":
                return httpx.Response(204)
            return json_response({"data": [mock_invitation]})

        client = make_async_client(handler)
        await client.members.invite({"email": "bob@acme.com", "role": "admin", "mailbox_access": "all"})
        assert (await client.members.list_invitations())["data"] == [mock_invitation]
        assert await client.members.cancel_invitation("inv_bob") is None
        assert calls == [
            "POST /v1/members/invitations",
            "GET /v1/members/invitations",
            "DELETE /v1/members/invitations/inv_bob",
        ]

    @pytest.mark.asyncio
    async def test_grants_and_revokes_mailbox_access(self) -> None:
        calls: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            calls.append(f"{request.method} {request.url.path}")
            return json_response(mock_member)

        client = make_async_client(handler)
        assert await client.members.grant_mailbox_access("mem_alice", "mbx_sales") == mock_member
        assert await client.members.revoke_mailbox_access("mem_alice", "mbx_sales") == mock_member
        assert calls == [
            "PUT /v1/members/mem_alice/mailboxes/mbx_sales",
            "DELETE /v1/members/mem_alice/mailboxes/mbx_sales",
        ]
