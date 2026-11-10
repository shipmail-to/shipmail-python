from __future__ import annotations

import json

import httpx
import pytest

from tests.conftest import json_response, make_async_client, make_client

DEFINITION = {
    "trigger": {"type": "scheduled", "cron": "0 8 * * *", "time_zone": "Europe/Lisbon"},
    "conditions": [],
    "actions": [
        {"type": "generate_mail_report", "metric": "received", "lookback_minutes": 1440}
    ],
    "mode": "draft",
    "scope": {"mailbox_ids": ["mbx_1"], "calendar_addresses": []},
}
AUTOMATION = {
    "object": "automation",
    "id": "aaut_abcdefghijklmnopqrstuvwx",
    "name": "Daily brief",
    "status": "active",
    "version_id": "aav_1",
    "version": 1,
    "definition": DEFINITION,
    "last_run": None,
    "next_run_at": None,
    "runnable": True,
    "blocked_reasons": [],
    "send_degraded_reasons": [],
    "created_at": "2026-08-02T00:00:00.000Z",
    "updated_at": "2026-08-02T00:00:00.000Z",
}


def test_sync_automations_cover_the_public_endpoints() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/run"):
            return json_response(
                {
                    "object": "automation_run",
                    "id": "aar_1",
                    "automation_id": AUTOMATION["id"],
                    "status": "queued",
                },
                202,
            )
        if request.method == "POST":
            assert json.loads(request.content) == {"name": "Daily brief", "definition": DEFINITION}
        is_list = request.url.path.endswith("automations") and request.method == "GET"
        return json_response({"data": [AUTOMATION]} if is_list else AUTOMATION)

    client = make_client(handler)
    assert client.automations.list()["data"][0]["id"] == AUTOMATION["id"]
    assert client.automations.create({"name": "Daily brief", "definition": DEFINITION})["status"] == "active"
    assert client.automations.get(AUTOMATION["id"])["name"] == "Daily brief"
    assert client.automations.update(AUTOMATION["id"], {"status": "paused"})["id"] == AUTOMATION["id"]
    assert client.automations.run(AUTOMATION["id"])["status"] == "queued"
    assert [request.method for request in requests] == ["GET", "POST", "GET", "PATCH", "POST"]


@pytest.mark.asyncio
async def test_async_automations_use_the_same_contract() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/run"):
            return json_response(
                {
                    "object": "automation_run",
                    "id": "aar_1",
                    "automation_id": AUTOMATION["id"],
                    "status": "queued",
                },
                202,
            )
        return json_response({"data": [AUTOMATION]} if request.url.path.endswith("automations") else AUTOMATION)

    client = make_async_client(handler)
    assert (await client.automations.list())["data"][0]["id"] == AUTOMATION["id"]
    assert (await client.automations.run(AUTOMATION["id"]))["status"] == "queued"
    assert [request.method for request in requests] == ["GET", "POST"]


TEST_RESULT = {
    "object": "automation_test",
    "automation_id": AUTOMATION["id"],
    "mailbox_id": "mbx_1",
    "message_id": "eml_1",
    "runnable": True,
    "blocked_reasons": [],
    "send_degraded_reasons": [],
    "conditions": [],
    "conditions_matched": True,
    "would_run": True,
    "mode": "draft",
    "actions": [{"index": 0, "type": "generate_mail_report"}],
    "model_calls": 0,
}


def test_tests_an_automation_on_a_message() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == f"/v1/automations/{AUTOMATION['id']}/test"
        assert json.loads(request.content) == {"mailbox_id": "mbx_1", "message_id": "eml_1"}
        return json_response(TEST_RESULT)

    client = make_client(handler)
    assert client.automations.test(AUTOMATION["id"], {"mailbox_id": "mbx_1", "message_id": "eml_1"}) == TEST_RESULT


@pytest.mark.asyncio
async def test_tests_an_automation_on_a_message_async() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == f"/v1/automations/{AUTOMATION['id']}/test"
        return json_response(TEST_RESULT)

    client = make_async_client(handler)
    result = await client.automations.test(AUTOMATION["id"], {"mailbox_id": "mbx_1", "message_id": "eml_1"})
    assert result["would_run"] is True
