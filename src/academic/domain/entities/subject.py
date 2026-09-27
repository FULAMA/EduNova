from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Subject:
    id: UUID
    tenant_id: UUID
    name: str
    code: str
    coefficient: float
    active: bool = True

    def __post_init__(self):
        if self.tenant_id is None:
            raise ValueError("Le tenant est obligatoire.")

        if not self.name.strip():
            raise ValueError("Le nom de la matière ne peut pas être vide.")

        if not self.code.strip():
            raise ValueError("Le code de la matière ne peut pas être vide.")

        if self.coefficient <= 0:
            raise ValueError("Le coefficient doit être supérieur à zéro.")
