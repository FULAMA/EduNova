from uuid import UUID

from pydantic import BaseModel, Field


class AddSubjectResultRequestSchema(BaseModel):
    subject_id: UUID
    average: float = Field(ge=0, le=20)
    coefficient: float = Field(gt=0)
