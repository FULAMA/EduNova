from uuid import UUID

from src.application.context.tenant_context import TenantContext
from src.application.interfaces.membership_repository import (
    MembershipRepository,
)


class SelectTenant:

    def __init__(
        self,
        membership_repository: MembershipRepository,
    ):
        self.membership_repository = membership_repository

    def execute(
        self,
        user_id: UUID,
        tenant_id: UUID,
    ) -> TenantContext:

        membership = (
            self.membership_repository.find_by_user_and_tenant(
                user_id,
                tenant_id,
            )
        )

        if membership is None:
            raise ValueError(
                "L'utilisateur n'est pas membre de ce tenant."
            )

        if not membership.active:
            raise ValueError(
                "Le membership n'est pas actif."
            )

        return TenantContext(tenant_id)
