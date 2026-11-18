from uuid import UUID

from pydantic import BaseModel


class TenantOptionSchema(BaseModel):
    tenant_id: UUID
    tenant_name: str
    tenant_slug: str
    role: str


class LoginUserResponse(BaseModel):
    authenticated: bool
    two_factor_required: bool
    two_factor_token: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    email: str | None = None
    tenant_selection_required: bool = False
    tenant_selection_token: str | None = None
    available_tenants: list[TenantOptionSchema] = []
