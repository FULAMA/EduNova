from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AddSubjectResultRequestSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    subject_id: UUID
    average: float = Field(ge=0, le=20)
