from uuid import UUID

from pydantic import BaseModel


class CreateAcademicRecordResponse(BaseModel):
    student_id: UUID
    academic_period_id: UUID
    general_average: float
    failed_subjects: int
    credits_obtained: float
    total_credits: float
