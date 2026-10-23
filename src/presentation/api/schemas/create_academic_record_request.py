from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateAcademicRecordRequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    student_id: UUID
    academic_period_id: UUID
    total_credits: float = Field(gt=0)
