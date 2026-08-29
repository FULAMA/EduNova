from uuid import UUID

from pydantic import BaseModel


class SubjectResultResponse(BaseModel):
    subject_id: UUID
    average: float
    coefficient: float


class AcademicRecordResponse(BaseModel):
    student_id: UUID
    academic_period_id: UUID
    general_average: float
    failed_subjects: int
    credits_obtained: float
    total_credits: float
    subject_results: list[SubjectResultResponse]
