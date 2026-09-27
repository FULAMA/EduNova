from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RegisterUserResponse:
    id: UUID
    email: str
    role: str
    is_active: bool
    two_factor_enabled: bool
