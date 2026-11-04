from __future__ import annotations

from typing import List, Literal, Optional, TypedDict

SmtpCredentialPortSecurity = Literal["tls", "starttls"]


class SmtpCredentialPort(TypedDict):
    port: int
    security: SmtpCredentialPortSecurity


# Sends only as `from`, one transactional sender's address.
SmtpCredential = TypedDict(
    "SmtpCredential",
    {
        "object": Literal["smtp_credential"],
        "id": str,
        "from": str,
        "name": str,
        "username": str,
        "host": str,
        "ports": List[SmtpCredentialPort],
        "last_used_at": Optional[str],
        "created_at": str,
    },
)

# The password is returned once. Shipmail keeps no copy.
CreatedSmtpCredential = TypedDict(
    "CreatedSmtpCredential",
    {
        "object": Literal["smtp_credential"],
        "id": str,
        "from": str,
        "name": str,
        "username": str,
        "host": str,
        "ports": List[SmtpCredentialPort],
        "last_used_at": Optional[str],
        "created_at": str,
        "password": str,
    },
)


class SmtpCredentialList(TypedDict):
    object: Literal["list"]
    data: List[SmtpCredential]


ListSmtpCredentialsParams = TypedDict("ListSmtpCredentialsParams", {"from": str}, total=False)

CreateSmtpCredentialParams = TypedDict("CreateSmtpCredentialParams", {"from": str, "name": str})
