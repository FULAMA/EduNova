from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RegisterEstablishmentResponse:
    """Application DTO returned after successful establishment provisioning.

    Contains public confirmation identifiers for the newly provisioned
    tenant, user, and administrative membership. Sensitive data such as
    passwords, password hashes, or two-factor secrets are never included.
    """

    tenant_id: UUID
    tenant_name: str
    tenant_slug: str
    user_id: UUID
    admin_name: str
    email: str
    role: str
