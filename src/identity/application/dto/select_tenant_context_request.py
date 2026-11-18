from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class SelectTenantContextRequest:
    """DTO required to select an establishment context using a temporary token."""

    tenant_selection_token: str
    tenant_id: UUID
