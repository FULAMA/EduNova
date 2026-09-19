from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects.subject_result import SubjectResult


@dataclass(frozen=True)
class StudentAcademicRecord:
    tenant_id: UUID
    student_id: UUID
    academic_period_id: UUID
    subject_results: tuple[SubjectResult, ...]
    general_average: float
    failed_subjects: int
    credits_obtained: float
    total_credits: float

    def __post_init__(self):
        if self.tenant_id is None:
            raise ValueError("Le tenant est obligatoire.")

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

    def with_subject_result(
        self,
        subject_result: SubjectResult,
    ) -> "StudentAcademicRecord":
        new_subject_results = self.subject_results + (subject_result,)

        total_coefficients = sum(
            result.coefficient
            for result in new_subject_results
        )

        weighted_sum = sum(
            result.average * result.coefficient
            for result in new_subject_results
        )

        general_average = weighted_sum / total_coefficients

        failed_subjects = sum(
            1
            for result in new_subject_results
            if result.average < 10
        )

        return StudentAcademicRecord(
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_period_id=self.academic_period_id,
            subject_results=new_subject_results,
            general_average=general_average,
            failed_subjects=failed_subjects,
            credits_obtained=self.credits_obtained,
            total_credits=self.total_credits,
        )
