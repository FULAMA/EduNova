from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AddSubjectResultRequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject_id: UUID
    average: float = Field(ge=0, le=20)
    coefficient: float = Field(gt=0)
