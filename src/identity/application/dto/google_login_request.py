from uuid import UUID

from dataclasses import dataclass


@dataclass(frozen=True)
class GoogleLoginRequest:
    id_token: str
    tenant_id: UUID
