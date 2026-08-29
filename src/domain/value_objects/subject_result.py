from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SubjectResult:
    subject_id: UUID
    average: float
    coefficient: float

    def __post_init__(self):
        if not 0 <= self.average <= 20:
            raise ValueError(
                "La moyenne doit être comprise entre 0 et 20."
            )

        if self.coefficient <= 0:
            raise ValueError(
                "Le coefficient doit être supérieur à zéro."
            )