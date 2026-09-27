from dataclasses import dataclass
from uuid import UUID

from src.academic.application.dto.subject_result_response import (
    SubjectResultResponse,
)


@dataclass(frozen=True)
class CreateAcademicRecordResponse:
    student_id: UUID
    academic_period_id: UUID
    subject_results: tuple[SubjectResultResponse, ...]
    general_average: float
    failed_subjects: int
    credits_obtained: float
    total_credits: float
