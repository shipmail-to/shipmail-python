from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from .._base_client import RequestOptions

if TYPE_CHECKING:
    from .._client import AsyncShipmail, Shipmail
    from .._types.automation import (
        Automation,
        AutomationRun,
        AutomationTest,
        CreateAutomationParams,
        ListAutomationsResponse,
        TestAutomationParams,
        UpdateAutomationParams,
    )
    from .._types.common import MethodOptions


def _automation(automation_id: str) -> str:
    return f"/automations/{quote(automation_id, safe='')}"


class SyncAutomations:
    def __init__(self, client: Shipmail) -> None:
        self._client = client

    def list(self, options: MethodOptions | None = None) -> ListAutomationsResponse:
        return self._client.request(
            RequestOptions(method="GET", path="/automations", method_options=options)
        )

    def create(
        self, params: CreateAutomationParams, options: MethodOptions | None = None
    ) -> Automation:
        return self._client.request(
            RequestOptions(method="POST", path="/automations", body=params, method_options=options)
        )

    def get(self, id: str, options: MethodOptions | None = None) -> Automation:
        return self._client.request(
            RequestOptions(method="GET", path=_automation(id), method_options=options)
        )

    def update(
        self, id: str, params: UpdateAutomationParams, options: MethodOptions | None = None
    ) -> Automation:
        return self._client.request(
            RequestOptions(
                method="PATCH", path=_automation(id), body=params, method_options=options
            )
        )

    def test(
        self, id: str, params: TestAutomationParams, options: MethodOptions | None = None
    ) -> AutomationTest:
        """Dry-run the automation on one stored inbox message. Nothing is changed, queued or sent.

        Needs automations:read and messages:read. A semantic condition calls the classifier only when
        every other condition matched, and that call counts against the AI budget.
        """
        return self._client.request(
            RequestOptions(method="POST", path=f"{_automation(id)}/test", body=params, method_options=options)
        )

    def run(self, id: str, options: MethodOptions | None = None) -> AutomationRun:
        return self._client.request(
            RequestOptions(method="POST", path=f"{_automation(id)}/run", method_options=options)
        )


class AsyncAutomations:
    def __init__(self, client: AsyncShipmail) -> None:
        self._client = client

    async def list(self, options: MethodOptions | None = None) -> ListAutomationsResponse:
        return await self._client.request(
            RequestOptions(method="GET", path="/automations", method_options=options)
        )

    async def create(
        self, params: CreateAutomationParams, options: MethodOptions | None = None
    ) -> Automation:
        return await self._client.request(
            RequestOptions(method="POST", path="/automations", body=params, method_options=options)
        )

    async def get(self, id: str, options: MethodOptions | None = None) -> Automation:
        return await self._client.request(
            RequestOptions(method="GET", path=_automation(id), method_options=options)
        )

    async def update(
        self, id: str, params: UpdateAutomationParams, options: MethodOptions | None = None
    ) -> Automation:
        return await self._client.request(
            RequestOptions(
                method="PATCH", path=_automation(id), body=params, method_options=options
            )
        )

    async def test(
        self, id: str, params: TestAutomationParams, options: MethodOptions | None = None
    ) -> AutomationTest:
        """Dry-run the automation on one stored inbox message. Nothing is changed, queued or sent.

        Needs automations:read and messages:read. A semantic condition calls the classifier only when
        every other condition matched, and that call counts against the AI budget.
        """
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_automation(id)}/test", body=params, method_options=options)
        )

    async def run(self, id: str, options: MethodOptions | None = None) -> AutomationRun:
        return await self._client.request(
            RequestOptions(method="POST", path=f"{_automation(id)}/run", method_options=options)
        )
