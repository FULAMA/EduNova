from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class AcademicPeriod:
    id: UUID
    name: str
    start_date: date
    end_date: date

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError(
                "Le nom de la période académique ne peut pas être vide."
            )

        if self.end_date <= self.start_date:
            raise ValueError(
                "La date de fin doit être postérieure "
                "à la date de début."
            )

    def contains(self, target_date: date) -> bool:
        return self.start_date <= target_date <= self.end_date