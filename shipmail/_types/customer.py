from __future__ import annotations

from typing import Dict, List, Literal, Optional, TypedDict, Union

from .common import PaginationParams

CustomerIdentifierKind = Literal["email", "domain"]
CustomerFieldValue = Union[str, int, float, bool]
CustomerFieldType = Literal["text", "number", "date", "url", "boolean"]
ReplyTargetState = Literal["on_track", "at_risk", "missed"]


class CustomerIdentifier(TypedDict):
    kind: CustomerIdentifierKind
    value: str


class CustomerExternalId(TypedDict):
    # Lowercase slug of the system that knows the customer, such as "hubspot" or "stripe".
    source: str
    external_id: str
    url: Optional[str]


class Customer(TypedDict):
    object: Literal["customer"]
    id: str
    name: Optional[str]
    company: Optional[str]
    notes: Optional[str]
    # The reply time this customer gets. None means the mailbox default.
    service_level_id: Optional[str]
    fields: Dict[str, CustomerFieldValue]
    # Free-form labels such as "vip", stored lowercase. Empty when the customer has none.
    tags: List[str]
    identifiers: List[CustomerIdentifier]
    external_ids: List[CustomerExternalId]
    created_at: str
    updated_at: str


class ListCustomersParams(PaginationParams, total=False):
    email: str
    domain: str
    # Give with external_id.
    external_source: str
    external_id: str
    # Searches name, company and identifiers.
    q: str
    # Customers with this tag, matched after normalization, so "VIP" finds "vip".
    tag: str


class _CustomerExternalIdInputRequired(TypedDict):
    source: str
    external_id: str


class CustomerExternalIdInput(_CustomerExternalIdInputRequired, total=False):
    url: Optional[str]


class _CustomerProfileParams(TypedDict, total=False):
    name: Optional[str]
    company: Optional[str]
    notes: Optional[str]
    service_level_id: Optional[str]
    fields: Dict[str, CustomerFieldValue]
    # Replaces the whole list when given; trimmed, lowercased and deduplicated. At most 20 tags of
    # 1 to 32 characters, without commas.
    tags: List[str]
    # Replaces the whole set when given.
    identifiers: List[CustomerIdentifier]


class CreateCustomerParams(_CustomerProfileParams, total=False):
    # Replaces the whole set when given.
    external_ids: List[CustomerExternalIdInput]


UpdateCustomerParams = CreateCustomerParams


class UpsertCustomerParams(_CustomerProfileParams, total=False):
    # Link to the record in the external system.
    url: Optional[str]


class BusinessHoursInterval(TypedDict):
    # 0 is Sunday.
    day: int
    start: str
    end: str


class BusinessHours(TypedDict):
    time_zone: str
    days: List[BusinessHoursInterval]


class ServiceLevel(TypedDict):
    object: Literal["service_level"]
    id: str
    name: str
    reply_target_minutes: int
    # None when the clock always runs.
    business_hours: Optional[BusinessHours]
    position: int
    created_at: str
    updated_at: str


class CustomerField(TypedDict):
    object: Literal["customer_field"]
    id: str
    key: str
    label: str
    type: CustomerFieldType
    position: int
    created_at: str
    updated_at: str


class ServiceLevelList(TypedDict):
    data: List[ServiceLevel]


class CustomerFieldList(TypedDict):
    data: List[CustomerField]


class ReplyTarget(TypedDict):
    state: ReplyTargetState
    service_level_id: Optional[str]
    started_at: str
    warn_at: str
    due_at: str
