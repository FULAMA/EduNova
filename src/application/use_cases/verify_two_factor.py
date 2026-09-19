from uuid import UUID

from src.application.interfaces.membership_repository import (
    MembershipRepository,
)
from src.application.interfaces.user_repository import (
    UserRepository,
)
from src.application.services.two_factor_service import (
    TwoFactorService,
)


class VerifyTwoFactor:

    def __init__(
        self,
        user_repository: UserRepository,
        membership_repository: MembershipRepository,
        two_factor_service: TwoFactorService,
    ):
        self._user_repository = user_repository
        self._membership_repository = membership_repository
        self._two_factor_service = two_factor_service

    def execute(
        self,
        user_id: UUID,
        tenant_id: UUID,
        code: str,
    ) -> bool:

        membership = (
            self._membership_repository.find_by_user_and_tenant(
                user_id,
                tenant_id,
            )
        )

        if membership is None or not membership.active:
            raise ValueError(
                "Utilisateur introuvable."
            )

        user = self._user_repository.find_by_id(user_id)

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        if not user.two_factor_secret:
            raise ValueError(
                "Le 2FA n est pas configure."
            )

        is_valid = self._two_factor_service.verify_code(
            secret=user.two_factor_secret,
            code=code,
        )

        if not is_valid:
            raise ValueError(
                "Code 2FA invalide."
            )

        user.two_factor_enabled = True

        self._user_repository.save(user)

        return True
