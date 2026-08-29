from dataclasses import dataclass
from uuid import UUID


@dataclass
class Subject:
    id: UUID
    code: str
    name: str
    coefficient: float
    credits: int = 0
    is_active: bool = True

    def __post_init__(self):
        self.code = self.code.strip().upper()
        self.name = self.name.strip()

        if not self.code:
            raise ValueError(
                "Le code de la matière ne peut pas être vide."
            )

        if not self.name:
            raise ValueError(
                "Le nom de la matière ne peut pas être vide."
            )

        if self.coefficient <= 0:
            raise ValueError(
                "Le coefficient doit être supérieur à zéro."
            )

        if self.credits < 0:
            raise ValueError(
                "Le nombre de crédits ne peut pas être négatif."
            )

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False