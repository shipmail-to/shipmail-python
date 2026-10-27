from __future__ import annotations

from typing import Literal, TypedDict

from .common import PaginationParams

TemplateVariableValues = dict[str, str | int | float | bool]


class TemplateVariable(TypedDict):
    key: str
    required: bool
    fallback: str | None


class Template(TypedDict):
    object: Literal["template"]
    id: str
    name: str
    subject: str
    html: str | None
    text: str | None
    fallbacks: dict[str, str]
    variables: list[TemplateVariable]
    published_version: int | None
    has_unpublished_changes: bool
    created_at: str
    updated_at: str


class TemplateVersion(TypedDict):
    object: Literal["template_version"]
    template_id: str
    version: int
    subject: str
    html: str | None
    text: str | None
    fallbacks: dict[str, str]
    variables: list[TemplateVariable]
    published_at: str


class _CreateTemplateParamsRequired(TypedDict):
    name: str
    subject: str


class CreateTemplateParams(_CreateTemplateParamsRequired, total=False):
    html: str
    text: str
    fallbacks: dict[str, str]
    publish: bool


class UpdateTemplateParams(TypedDict, total=False):
    name: str
    subject: str
    html: str | None
    text: str | None
    fallbacks: dict[str, str]


ListTemplatesParams = PaginationParams
ListTemplateVersionsParams = PaginationParams


class RenderTemplateParams(TypedDict, total=False):
    variables: TemplateVariableValues
    version: int


class RenderedTemplate(TypedDict):
    object: Literal["rendered_template"]
    template_id: str
    version: int | None
    subject: str
    html: str | None
    text: str | None


class _SendMessageTemplateRequired(TypedDict):
    id: str


class SendMessageTemplate(_SendMessageTemplateRequired, total=False):
    version: int
    variables: TemplateVariableValues
