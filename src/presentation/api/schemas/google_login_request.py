from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GoogleLoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id_token: str = Field(min_length=1)
    tenant_id: UUID
    nonce: str = Field(min_length=1, max_length=256)
