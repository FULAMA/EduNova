from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SelectTenantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_selection_token: str = Field(min_length=10)
    tenant_id: UUID
