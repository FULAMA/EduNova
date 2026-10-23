from dataclasses import dataclass
from enum import Enum
import math
from uuid import UUID

from src.academic.domain.value_objects.subject_result import SubjectResult
from src.academic.domain.policies.academic_policy import AcademicPolicy
from src.academic.domain.services.academic_average_calculator import (
    AcademicAverageCalculator,
)


class AcademicRecordStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"


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
    status: AcademicRecordStatus = AcademicRecordStatus.DRAFT
    version: int = 1

    def __post_init__(self):
        if self.tenant_id is None:
            raise ValueError("Le tenant est obligatoire.")

        if self.version <= 0:
            raise ValueError(
                "La version doit Ãªtre supÃ©rieure Ã  zÃ©ro."
            )

        if not math.isfinite(self.general_average) or not 0 <= self.general_average <= 20:
            raise ValueError(
                "La moyenne gÃ©nÃ©rale doit Ãªtre comprise entre 0 et 20."
            )

        if self.failed_subjects < 0:
            raise ValueError(
                "Le nombre de matiÃ¨res Ã©chouÃ©es ne peut pas Ãªtre nÃ©gatif."
            )

        if not math.isfinite(self.credits_obtained) or self.credits_obtained < 0:
            raise ValueError(
                "Les crÃ©dits obtenus ne peuvent pas Ãªtre nÃ©gatifs."
            )

        if not math.isfinite(self.total_credits) or self.total_credits <= 0:
            raise ValueError(
                "Le total des crÃ©dits doit Ãªtre supÃ©rieur Ã  zÃ©ro."
            )

        if self.credits_obtained > self.total_credits:
            raise ValueError(
                "Les crÃ©dits obtenus ne peuvent pas dÃ©passer "
                "le total des crÃ©dits."
            )

    def validate(self) -> "StudentAcademicRecord":
        if self.status == AcademicRecordStatus.VALIDATED:
            raise ValueError(
                "Le relevÃ© acadÃ©mique est dÃ©jÃ  validÃ©."
            )

        return StudentAcademicRecord(
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_period_id=self.academic_period_id,
            subject_results=self.subject_results,
            general_average=self.general_average,
            failed_subjects=self.failed_subjects,
            credits_obtained=self.credits_obtained,
            total_credits=self.total_credits,
            status=AcademicRecordStatus.VALIDATED,
            version=self.version + 1,
        )

    def with_subject_result(
        self,
        subject_result: SubjectResult,
        *,
        policy: AcademicPolicy | None = None,
        average_calculator: AcademicAverageCalculator | None = None,
    ) -> "StudentAcademicRecord":
        if self.status == AcademicRecordStatus.VALIDATED:
            raise ValueError(
                "Un relevÃ© acadÃ©mique validÃ© ne peut pas Ãªtre modifiÃ©."
            )

        if any(
            result.subject_id == subject_result.subject_id
            for result in self.subject_results
        ):
            raise ValueError(
                "Un rÃ©sultat existe dÃ©jÃ  pour cette matiÃ¨re."
            )

        new_subject_results = self.subject_results + (subject_result,)
        general_average, failed_subjects = self.calculate_aggregates(
            new_subject_results,
            policy=policy,
            average_calculator=average_calculator,
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
            status=self.status,
            version=self.version + 1,
        )

    @staticmethod
    def calculate_aggregates(
        subject_results: tuple[SubjectResult, ...],
        *,
        policy: AcademicPolicy | None = None,
        average_calculator: AcademicAverageCalculator | None = None,
    ) -> tuple[float, int]:
        policy = policy or AcademicPolicy()
        average_calculator = average_calculator or AcademicAverageCalculator()
        average = policy.round_average(
            average_calculator.calculate(subject_results)
        )
        failed_subjects = sum(
            not policy.is_subject_passed(result.average)
            for result in subject_results
        )
        return average, failed_subjects
    def create_new_version(
        self,
        general_average: float,
        failed_subjects: int,
        credits_obtained: float,
    ) -> "StudentAcademicRecord":
        if self.status != AcademicRecordStatus.VALIDATED:
            raise ValueError(
                "Seul un relevÃ© validÃ© peut faire l'objet d'une correction."
            )

        return StudentAcademicRecord(
            tenant_id=self.tenant_id,
            student_id=self.student_id,
            academic_period_id=self.academic_period_id,
            subject_results=self.subject_results,
            general_average=general_average,
            failed_subjects=failed_subjects,
            credits_obtained=credits_obtained,
            total_credits=self.total_credits,
            status=AcademicRecordStatus.VALIDATED,
            version=self.version + 1,
        )
