from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Membership:
    id: UUID
    user_id: UUID
    tenant_id: UUID
    role: str
    active: bool = True

    def __post_init__(self):
        if not self.role.strip():
            raise ValueError("Le role ne peut pas etre vide.")
