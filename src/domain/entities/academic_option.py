from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class AcademicOption:
    id: UUID
    name: str
    code: str
    active: bool = True

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError(
                "Le nom de l'option ne peut pas être vide."
            )

        if not self.code.strip():
            raise ValueError(
                "Le code de l'option ne peut pas être vide."
            )
