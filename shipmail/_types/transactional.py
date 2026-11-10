from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

TransactionalDomainStatus = Literal["pending", "verifying", "verified", "failed"]
TransactionalDnsRecordStatus = Literal["pending", "verified", "failed"]
TransactionalSenderState = Literal["active", "disabled", "revoked"]


class TransactionalDnsRecord(TypedDict):
    key: str
    type: str
    host: str
    value: str
    priority: Optional[int]
    ttl: Optional[int]
    description: str
    status: TransactionalDnsRecordStatus


# `dns_records` is empty until setup finishes. Create it again with the same values to resume.
class TransactionalDomain(TypedDict):
    object: Literal["transactional_domain"]
    id: str
    name: str
    root_domain: str
    status: TransactionalDomainStatus
    mail_from_domain: str
    dns_records: List[TransactionalDnsRecord]
    verified_at: Optional[str]
    created_at: str


class TransactionalDomainList(TypedDict):
    object: Literal["list"]
    data: List[TransactionalDomain]


class CreateTransactionalDomainParams(TypedDict):
    root_domain: str
    subdomain: str


TransactionalSender = TypedDict(
    "TransactionalSender",
    {
        "object": Literal["transactional_sender"],
        "id": str,
        "from": str,
        "display_name": str,
        "domain_id": Optional[str],
        "mailbox_id": str,
        "reply_to": str,
        "state": TransactionalSenderState,
        "refuse_disposable": bool,
        "smtp_enabled": bool,
        "created_at": str,
    },
)


class TransactionalSenderList(TypedDict):
    object: Literal["list"]
    data: List[TransactionalSender]


class ListTransactionalSendersParams(TypedDict, total=False):
    domain_id: str


class CreateTransactionalSenderParams(TypedDict):
    domain_id: str
    mailbox_id: str
    local_part: str
    display_name: str


# At least one field. A move applies first, then `state`, then `refuse_disposable`.
class UpdateTransactionalSenderParams(TypedDict, total=False):
    state: Literal["active", "disabled"]
    mailbox_id: str
    refuse_disposable: bool
