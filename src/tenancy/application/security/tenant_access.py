from uuid import UUID


class TenantAccess:

    def __init__(self, tenant_id: UUID | None):
        if tenant_id is None:
            raise ValueError("Le tenant actif est obligatoire.")

        self.tenant_id = tenant_id

    def allows(self, tenant_id: UUID) -> bool:
        return self.tenant_id == tenant_id
