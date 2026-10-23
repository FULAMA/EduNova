from uuid import UUID

from pydantic import BaseModel


class StudentSummaryResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str | None
    active: bool
