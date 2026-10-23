from uuid import UUID

from pydantic import BaseModel


class AcademicClassResponse(BaseModel):
    id: UUID
    name: str
    active: bool
