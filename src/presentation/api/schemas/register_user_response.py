from uuid import UUID

from pydantic import BaseModel


class RegisterUserResponse(BaseModel):
    id: UUID
    email: str
    role: str
    is_active: bool
    two_factor_enabled: bool
