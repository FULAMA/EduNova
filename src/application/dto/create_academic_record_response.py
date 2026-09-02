from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects.subject_result import SubjectResult


@dataclass(frozen=True)
class CreateAcademicRecordResponse:
    student_id: UUID
    academic_period_id: UUID
    subject_results: tuple[SubjectResult, ...]
    general_average: float
    failed_subjects: int
    credits_obtained: float
    total_credits: float
