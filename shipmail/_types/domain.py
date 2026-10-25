from __future__ import annotations

from typing import Literal, TypedDict

from .common import DomainStatus, PaginationParams


class _DomainRequired(TypedDict):
    object: Literal["domain"]
    id: str
    name: str
    status: DomainStatus
    managed_by: Literal["external", "shipmail"]
    dns_provider: str | None
    mx_verified: bool
    spf_verified: bool
    dkim_verified: bool
    dmarc_verified: bool
    dmarc_managed_externally: bool
    outbound_verified: bool
    catch_all_mailbox_id: str | None
    verified_at: str | None
    created_at: str
    updated_at: str


class Domain(_DomainRequired, total=False):
    registration: DomainRegistrationInfo


class CreateDomainParams(TypedDict):
    name: str


class UpdateDomainParams(TypedDict):
    catch_all_mailbox_id: str | None


ListDomainsParams = PaginationParams


class DomainVerificationRecords(TypedDict):
    mx: bool
    spf: bool
    dkim: bool
    dmarc: bool


class DomainVerificationResult(TypedDict):
    all_verified: bool
    records: DomainVerificationRecords
    outbound_verified: bool
    outbound_error: bool
    existing_spf: str | None
    suggested_spf: str | None
    conflicting_mx: list[str]
    dmarc_valid: bool
    dmarc_exact_match: bool
    dmarc_record_value: str | None
    dmarc_managed_externally: bool


DomainDnsRecordKey = Literal["mx", "spf", "mail_from_mx", "mail_from_spf", "dkim", "dmarc"]
DomainDnsRecordStatus = Literal["verified", "not_found", "mismatch", "pending"]


class DomainDnsRecord(TypedDict):
    key: DomainDnsRecordKey
    type: Literal["MX", "TXT"]
    host: str
    value: str | None
    priority: int | None
    ttl: int
    status: DomainDnsRecordStatus
    found_values: list[str]


class DomainDnsRecordSet(TypedDict):
    object: Literal["dns_record_set"]
    domain_id: str
    domain_name: str
    all_verified: bool
    checked_at: str
    records: list[DomainDnsRecord]


DomainHealthProvider = Literal["google", "microsoft", "yahoo", "apple", "other"]


class DomainHealthDns(TypedDict):
    mx: bool
    spf: bool
    dkim: bool
    dmarc: bool
    last_checked_at: str | None


class DomainHealthBlocklist(TypedDict):
    list: Literal["spamhaus_dbl"]
    listed: bool
    listed_since: str | None


class DomainHealthProviderDelivery(TypedDict):
    provider: DomainHealthProvider
    recipients: int
    delivered: int
    bounced: int
    deferred: int
    complained: int
    delivery_rate: float | None


class DomainHealthDelivery(TypedDict):
    since: str
    until: str
    recipients: int
    delivered: int
    bounced: int
    deferred: int
    complained: int
    failed: int
    suppressed: int
    queued: int
    sent: int
    delivery_rate: float | None
    providers: list[DomainHealthProviderDelivery]


class DomainHealth(TypedDict):
    object: Literal["domain_health"]
    domain_id: str
    domain: str
    generated_at: str
    dns: DomainHealthDns
    blocklist: DomainHealthBlocklist
    delivery: DomainHealthDelivery


class DomainSearchResult(TypedDict):
    domain_name: str
    available: bool
    purchase_price: float | None
    renewal_price: float | None
    currency: str
    premium: bool


class SearchDomainsParams(TypedDict):
    keyword: str


class _RegistrationContactRequired(TypedDict):
    first_name: str
    last_name: str
    address1: str
    city: str
    zip: str
    country: str
    phone: str
    email: str


class RegistrationContact(_RegistrationContactRequired, total=False):
    address2: str
    state: str


class _RegisterDomainParamsRequired(TypedDict):
    name: str
    contact: RegistrationContact


class RegisterDomainParams(_RegisterDomainParamsRequired, total=False):
    years: int


class DomainRegistrationInfo(TypedDict):
    expires_at: str
    auto_renew: bool
    renewal_price: float
    privacy_enabled: bool
    currency: str
    registered_at: str


class DomainSearchResponse(TypedDict):
    results: list[DomainSearchResult]
