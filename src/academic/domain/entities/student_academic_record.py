from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from src.academic.domain.value_objects.subject_result import SubjectResult


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

        if not 0 <= self.general_average <= 20:
            raise ValueError(
                "La moyenne gÃ©nÃ©rale doit Ãªtre comprise entre 0 et 20."
            )

        if self.failed_subjects < 0:
            raise ValueError(
                "Le nombre de matiÃ¨res Ã©chouÃ©es ne peut pas Ãªtre nÃ©gatif."
            )

        if self.credits_obtained < 0:
            raise ValueError(
                "Les crÃ©dits obtenus ne peuvent pas Ãªtre nÃ©gatifs."
            )

        if self.total_credits <= 0:
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
            version=self.version,
        )

    def with_subject_result(
        self,
        subject_result: SubjectResult,
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
            status=self.status,
            version=self.version,
        )
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
