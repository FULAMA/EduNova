from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Tenant:
    id: UUID
    name: str
    slug: str
    active: bool = True

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Le nom du tenant ne peut pas être vide.")

        if not self.slug.strip():
            raise ValueError("Le slug du tenant ne peut pas être vide.")
