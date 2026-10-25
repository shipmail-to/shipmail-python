from __future__ import annotations

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
