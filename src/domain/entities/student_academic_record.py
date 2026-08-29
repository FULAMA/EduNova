from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects.subject_result import SubjectResult


@dataclass(frozen=True)
class StudentAcademicRecord:
    student_id: UUID
    academic_period_id: UUID
    subject_results: tuple[SubjectResult, ...]
    general_average: float
    failed_subjects: int
    credits_obtained: float
    total_credits: float

    def __post_init__(self):
        if not 0 <= self.general_average <= 20:
            raise ValueError(
                "La moyenne générale doit être comprise entre 0 et 20."
            )

        if self.failed_subjects < 0:
            raise ValueError(
                "Le nombre de matières échouées ne peut pas être négatif."
            )

        if self.credits_obtained < 0:
            raise ValueError(
                "Les crédits obtenus ne peuvent pas être négatifs."
            )

        if self.total_credits <= 0:
            raise ValueError(
                "Le total des crédits doit être supérieur à zéro."
            )

        if self.credits_obtained > self.total_credits:
            raise ValueError(
                "Les crédits obtenus ne peuvent pas dépasser "
                "le total des crédits."
            )