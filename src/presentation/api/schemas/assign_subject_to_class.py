from uuid import UUID

from pydantic import BaseModel, Field


class AssignSubjectToClassRequestSchema(BaseModel):
    subject_id: UUID
    coefficient: float = Field(gt=0)
    academic_option_id: UUID | None = None
