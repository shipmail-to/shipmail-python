from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import httpx

from .conftest import json_response, make_client


class TestSyncPagination:
    def test_iterates_through_multiple_pages(self) -> None:
        request_count = {"value": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            request_count["value"] += 1
            parsed = urlparse(str(request.url))
            qs = parse_qs(parsed.query)
            cursor = qs.get("cursor", [None])[0]

            if cursor is None:
                return json_response({
                    "data": [
                        {"id": "1", "name": "first"},
                        {"id": "2", "name": "second"},
                    ],
                    "pagination": {"next_cursor": "cursor_page2", "has_more": True},
                })
            if cursor == "cursor_page2":
                return json_response({
                    "data": [{"id": "3", "name": "third"}],
                    "pagination": {"next_cursor": None, "has_more": False},
                })
            return json_response({
                "data": [],
                "pagination": {"next_cursor": None, "has_more": False},
            })

        client = make_client(handler)
        page = client.domains.list_auto_paginating(limit=2)
        items = list(page)

        assert len(items) == 3
        assert items[0]["id"] == "1"
        assert items[1]["id"] == "2"
        assert items[2]["id"] == "3"
        assert request_count["value"] == 2

    def test_stops_when_has_more_is_false_on_first_page(self) -> None:
        request_count = {"value": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            request_count["value"] += 1
            return json_response({
                "data": [{"id": "1", "name": "only"}],
                "pagination": {"next_cursor": None, "has_more": False},
            })

        client = make_client(handler)
        page = client.domains.list_auto_paginating()
        items = list(page)

        assert len(items) == 1
        assert request_count["value"] == 1

    def test_handles_empty_first_page(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return json_response({
                "data": [],
                "pagination": {"next_cursor": None, "has_more": False},
            })

        client = make_client(handler)
        page = client.domains.list_auto_paginating()
        items = list(page)

        assert len(items) == 0

    def test_passes_query_params_through(self) -> None:
        limit_values: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            qs = parse_qs(parsed.query)
            limit = qs.get("limit", [None])[0]
            if limit:
                limit_values.append(limit)

            cursor = qs.get("cursor", [None])[0]
            if cursor is None:
                return json_response({
                    "data": [{"id": "1", "name": "a"}],
                    "pagination": {"next_cursor": "c2", "has_more": True},
                })
            return json_response({
                "data": [{"id": "2", "name": "b"}],
                "pagination": {"next_cursor": None, "has_more": False},
            })

        client = make_client(handler)
        page = client.domains.list_auto_paginating(limit=5)
        items = list(page)

        assert len(items) == 2
        assert limit_values == ["5", "5"]

    def test_passes_cursor_from_previous_page(self) -> None:
        cursors_received: list[str | None] = []

        def handler(request: httpx.Request) -> httpx.Response:
            parsed = urlparse(str(request.url))
            qs = parse_qs(parsed.query)
            raw_cursor = qs.get("cursor", [None])[0]
            cursor = raw_cursor
            cursors_received.append(cursor)

            if len(cursors_received) == 1:
                return json_response({
                    "data": [{"id": "1", "name": "a"}],
                    "pagination": {"next_cursor": "page2_cursor", "has_more": True},
                })
            if len(cursors_received) == 2:
                return json_response({
                    "data": [{"id": "2", "name": "b"}],
                    "pagination": {"next_cursor": "page3_cursor", "has_more": True},
                })
            return json_response({
                "data": [{"id": "3", "name": "c"}],
                "pagination": {"next_cursor": None, "has_more": False},
            })

        client = make_client(handler)
        page = client.domains.list_auto_paginating()
        items = list(page)

        assert len(items) == 3
        assert cursors_received[0] is None
        assert cursors_received[1] == "page2_cursor"
        assert cursors_received[2] == "page3_cursor"
