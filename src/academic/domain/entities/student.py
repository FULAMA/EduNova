from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Student:
    id: UUID
    tenant_id: UUID
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    active: bool = True

    def __post_init__(self):
        if not self.first_name.strip():
            raise ValueError("Le prenom ne peut pas etre vide.")

        if not self.last_name.strip():
            raise ValueError("Le nom ne peut pas etre vide.")
