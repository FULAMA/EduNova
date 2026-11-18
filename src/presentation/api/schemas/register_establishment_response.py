from uuid import UUID

from pydantic import BaseModel


class RegisterEstablishmentResponse(BaseModel):
    tenant_id: UUID
    tenant_name: str
    tenant_slug: str
    user_id: UUID
    admin_name: str
    email: str
    role: str
