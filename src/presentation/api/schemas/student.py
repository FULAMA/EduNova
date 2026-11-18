from uuid import UUID

from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    registration_number: str | None = Field(default=None, max_length=50)


class StudentUpdateRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=254)
    phone: str | None = Field(default=None, max_length=40)
    registration_number: str | None = Field(default=None, max_length=50)
    active: bool = True


class StudentSummaryResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str | None
    registration_number: str | None = None
    active: bool


class StudentDuplicateCandidateResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    registration_number: str | None = None


class StudentCreatedResponse(StudentSummaryResponse):
    potential_duplicates: list[StudentDuplicateCandidateResponse] = Field(default_factory=list)
