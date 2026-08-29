from dataclasses import dataclass
from datetime import date
from uuid import UUID

from src.domain.value_objects.coefficient import Coefficient


@dataclass(frozen=True)
class Assessment:
    id: UUID
    subject_id: UUID
    title: str
    maximum_score: float
    coefficient: Coefficient
    assessment_date: date

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError(
                "Le titre de l'évaluation ne peut pas être vide."
            )

        if self.maximum_score <= 0:
            raise ValueError(
                "Le maximum de l'évaluation doit être supérieur à zéro."
            )