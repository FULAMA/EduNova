from dataclasses import dataclass
from uuid import UUID

from src.application.interfaces.user_repository import (
    UserRepository,
)
from src.application.services.two_factor_service import (
    TwoFactorService,
)


@dataclass(frozen=True)
class EnableTwoFactorResponse:
    secret: str
    provisioning_uri: str


class EnableTwoFactor:

    def __init__(
        self,
        user_repository: UserRepository,
        two_factor_service: TwoFactorService,
    ):
        self._user_repository = user_repository
        self._two_factor_service = two_factor_service

    def execute(
        self,
        user_id: UUID,
    ) -> EnableTwoFactorResponse:

        user = self._user_repository.find_by_id(user_id)

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        secret = self._two_factor_service.generate_secret()

        provisioning_uri = (
            self._two_factor_service.generate_provisioning_uri(
                email=user.email,
                secret=secret,
            )
        )

        user.two_factor_secret = secret
        user.two_factor_enabled = False

        self._user_repository.save(user)

        return EnableTwoFactorResponse(
            secret=secret,
            provisioning_uri=provisioning_uri,
        )
