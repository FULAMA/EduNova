from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AssignSubjectToClassRequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    subject_id: UUID
    coefficient: float = Field(gt=0)
    academic_option_id: UUID | None = None
