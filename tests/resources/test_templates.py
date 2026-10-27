from __future__ import annotations

import json

import httpx
import pytest

from shipmail import RenderedTemplate, Template, TemplateVersion
from tests.conftest import json_response, make_async_client, make_client

mock_template: Template = {
    "object": "template",
    "id": "tpl_123",
    "name": "Welcome",
    "subject": "Welcome, {{first_name}}",
    "html": "<p>Hi {{first_name}}, your plan is {{plan}}.</p>",
    "text": None,
    "fallbacks": {"plan": "Free"},
    "variables": [
        {"key": "first_name", "required": True, "fallback": None},
        {"key": "plan", "required": False, "fallback": "Free"},
    ],
    "published_version": 1,
    "has_unpublished_changes": False,
    "created_at": "2026-10-27T00:00:00Z",
    "updated_at": "2026-10-27T00:00:00Z",
}

mock_version: TemplateVersion = {
    "object": "template_version",
    "template_id": "tpl_123",
    "version": 1,
    "subject": "Welcome, {{first_name}}",
    "html": "<p>Hi {{first_name}}, your plan is {{plan}}.</p>",
    "text": None,
    "fallbacks": {"plan": "Free"},
    "variables": mock_template["variables"],
    "published_at": "2026-10-27T00:00:00Z",
}

mock_rendered: RenderedTemplate = {
    "object": "rendered_template",
    "template_id": "tpl_123",
    "version": None,
    "subject": "Welcome, Ada",
    "html": "<p>Hi Ada, your plan is Free.</p>",
    "text": None,
}

empty_page = {"data": [], "pagination": {"next_cursor": None, "has_more": False}}


class TestList:
    def test_sends_get_templates_with_cursor_and_limit(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/templates"
            assert request.url.params.get("cursor") == "cur_abc"
            assert request.url.params.get("limit") == "10"
            return json_response({**empty_page, "data": [mock_template]})

        client = make_client(handler)
        result = client.templates.list({"cursor": "cur_abc", "limit": 10})
        assert result["data"][0]["id"] == "tpl_123"

    def test_omits_query_without_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.query == b""
            return json_response(empty_page)

        client = make_client(handler)
        client.templates.list()

    def test_auto_paginates(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/templates"
            return json_response({**empty_page, "data": [mock_template]})

        client = make_client(handler)
        assert [t["id"] for t in client.templates.list_auto_paginating(limit=5)] == ["tpl_123"]

    @pytest.mark.asyncio
    async def test_async_lists(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/templates"
            return json_response({**empty_page, "data": [mock_template]})

        client = make_async_client(handler)
        result = await client.templates.list()
        assert result["data"][0]["name"] == "Welcome"


class TestCreate:
    def test_sends_post_templates_with_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/templates"
            assert json.loads(request.content) == {
                "name": "Welcome",
                "subject": "Welcome, {{first_name}}",
                "html": "<p>Hi {{first_name}}</p>",
                "fallbacks": {"plan": "Free"},
                "publish": True,
            }
            return json_response(mock_template, 201)

        client = make_client(handler)
        template = client.templates.create(
            {
                "name": "Welcome",
                "subject": "Welcome, {{first_name}}",
                "html": "<p>Hi {{first_name}}</p>",
                "fallbacks": {"plan": "Free"},
                "publish": True,
            }
        )
        assert template["published_version"] == 1
        assert template["variables"][0] == {"key": "first_name", "required": True, "fallback": None}

    @pytest.mark.asyncio
    async def test_async_creates(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert json.loads(request.content) == {"name": "Welcome", "subject": "Hi", "text": "Hello"}
            return json_response(mock_template, 201)

        client = make_async_client(handler)
        template = await client.templates.create({"name": "Welcome", "subject": "Hi", "text": "Hello"})
        assert template["id"] == "tpl_123"


class TestGet:
    def test_sends_get_with_encoded_id(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.raw_path == b"/v1/templates/tpl%2F123"
            return json_response(mock_template)

        client = make_client(handler)
        assert client.templates.get("tpl/123")["id"] == "tpl_123"

    @pytest.mark.asyncio
    async def test_async_gets(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/templates/tpl_123"
            return json_response(mock_template)

        client = make_async_client(handler)
        assert (await client.templates.get("tpl_123"))["name"] == "Welcome"


class TestUpdate:
    def test_sends_null_to_clear_a_body_and_omits_untouched_fields(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert request.url.path == "/v1/templates/tpl_123"
            assert json.loads(request.content) == {"subject": "Hello", "text": None}
            return json_response({**mock_template, "subject": "Hello", "has_unpublished_changes": True})

        client = make_client(handler)
        template = client.templates.update("tpl_123", {"subject": "Hello", "text": None})
        assert template["has_unpublished_changes"] is True

    @pytest.mark.asyncio
    async def test_async_updates(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "PATCH"
            assert json.loads(request.content) == {"html": None, "text": "Hi"}
            return json_response(mock_template)

        client = make_async_client(handler)
        await client.templates.update("tpl_123", {"html": None, "text": "Hi"})


class TestDelete:
    def test_sends_delete(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            assert request.url.path == "/v1/templates/tpl_123"
            return httpx.Response(204)

        client = make_client(handler)
        client.templates.delete("tpl_123")

    @pytest.mark.asyncio
    async def test_async_deletes(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "DELETE"
            return httpx.Response(204)

        client = make_async_client(handler)
        await client.templates.delete("tpl_123")


class TestPublish:
    def test_sends_post_publish(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/templates/tpl_123/publish"
            return json_response({**mock_template, "published_version": 2})

        client = make_client(handler)
        assert client.templates.publish("tpl_123")["published_version"] == 2

    @pytest.mark.asyncio
    async def test_async_publishes(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/templates/tpl_123/publish"
            return json_response(mock_template)

        client = make_async_client(handler)
        assert (await client.templates.publish("tpl_123"))["object"] == "template"


class TestRender:
    def test_sends_variables_and_version(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/templates/tpl_123/render"
            assert json.loads(request.content) == {
                "variables": {"first_name": "Ada", "seats": 3, "vip": True},
                "version": 1,
            }
            return json_response({**mock_rendered, "version": 1})

        client = make_client(handler)
        rendered = client.templates.render(
            "tpl_123", {"variables": {"first_name": "Ada", "seats": 3, "vip": True}, "version": 1}
        )
        assert rendered["version"] == 1

    def test_sends_an_empty_body_to_render_the_draft(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {}
            return json_response(mock_rendered)

        client = make_client(handler)
        rendered = client.templates.render("tpl_123")
        assert rendered["version"] is None
        assert rendered["subject"] == "Welcome, Ada"

    @pytest.mark.asyncio
    async def test_async_renders(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert json.loads(request.content) == {"variables": {"first_name": "Ada"}}
            return json_response(mock_rendered)

        client = make_async_client(handler)
        rendered = await client.templates.render("tpl_123", {"variables": {"first_name": "Ada"}})
        assert rendered["html"] == "<p>Hi Ada, your plan is Free.</p>"


class TestVersions:
    def test_lists_versions(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/templates/tpl_123/versions"
            assert request.url.params.get("limit") == "20"
            return json_response({**empty_page, "data": [mock_version]})

        client = make_client(handler)
        result = client.templates.list_versions("tpl_123", {"limit": 20})
        assert result["data"][0]["version"] == 1

    def test_auto_paginates_versions(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/templates/tpl_123/versions"
            return json_response({**empty_page, "data": [mock_version]})

        client = make_client(handler)
        assert [v["version"] for v in client.templates.list_versions_auto_paginating("tpl_123")] == [1]

    def test_gets_a_version(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "GET"
            assert request.url.path == "/v1/templates/tpl_123/versions/1"
            return json_response(mock_version)

        client = make_client(handler)
        assert client.templates.get_version("tpl_123", 1)["object"] == "template_version"

    def test_restores_a_version(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            assert request.url.path == "/v1/templates/tpl_123/versions/1/restore"
            return json_response({**mock_template, "has_unpublished_changes": True})

        client = make_client(handler)
        assert client.templates.restore_version("tpl_123", 1)["has_unpublished_changes"] is True

    @pytest.mark.asyncio
    async def test_async_version_methods(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            path = request.url.path
            if path == "/v1/templates/tpl_123/versions":
                return json_response({**empty_page, "data": [mock_version]})
            if path == "/v1/templates/tpl_123/versions/1":
                assert request.method == "GET"
                return json_response(mock_version)
            assert path == "/v1/templates/tpl_123/versions/1/restore"
            assert request.method == "POST"
            return json_response(mock_template)

        client = make_async_client(handler)
        listed = await client.templates.list_versions("tpl_123")
        assert listed["data"][0]["template_id"] == "tpl_123"
        assert (await client.templates.get_version("tpl_123", 1))["version"] == 1
        assert (await client.templates.restore_version("tpl_123", 1))["id"] == "tpl_123"
        assert [v["version"] async for v in client.templates.list_versions_auto_paginating("tpl_123")] == [1]
