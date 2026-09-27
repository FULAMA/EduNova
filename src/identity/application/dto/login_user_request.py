from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class LoginUserRequest:
    email: str
    password: str
    tenant_id: UUID
