from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LoginUserRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(min_length=3)
    password: str = Field(min_length=1)
    tenant_id: UUID
