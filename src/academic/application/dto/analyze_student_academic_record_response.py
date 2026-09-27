from dataclasses import dataclass
from uuid import UUID

from src.academic.application.dto.subject_result_response import (
    SubjectResultResponse,
)


@dataclass(frozen=True)
class AnalyzeStudentAcademicRecordResponse:
    student_id: UUID
    academic_period_id: UUID
    general_average: float
    failed_subjects: int
    credits_obtained: float
    total_credits: float
    subject_results: tuple[SubjectResultResponse, ...]
