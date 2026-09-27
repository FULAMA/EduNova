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
                "Le nom de la pÃ©riode acadÃ©mique ne peut pas Ãªtre vide."
            )

        if self.end_date <= self.start_date:
            raise ValueError(
                "La date de fin doit Ãªtre postÃ©rieure "
                "Ã  la date de dÃ©but."
            )

    def contains(self, target_date: date) -> bool:
        return self.start_date <= target_date <= self.end_date
