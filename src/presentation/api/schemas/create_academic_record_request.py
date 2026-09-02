from uuid import UUID

from pydantic import BaseModel


class CreateAcademicRecordRequestSchema(BaseModel):
    student_id: UUID
    academic_period_id: UUID
    total_credits: float
