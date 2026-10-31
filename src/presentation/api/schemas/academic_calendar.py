from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AcademicCalendarInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)


class AcademicCalendarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    description: str | None
    is_active: bool
