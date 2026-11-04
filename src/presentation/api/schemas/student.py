from uuid import UUID

from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)


class StudentSummaryResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str | None
    active: bool
