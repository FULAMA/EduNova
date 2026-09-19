from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CreateAcademicRecordRequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    student_id: UUID
    academic_period_id: UUID
    total_credits: float
