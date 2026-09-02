from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AcademicClass:
    id: UUID
    name: str
    active: bool = True

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError(
                "Le nom de la classe ne peut pas être vide."
            )
