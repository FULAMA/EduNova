from dataclasses import dataclass
from uuid import UUID

from src.application.interfaces.user_repository import (
    UserRepository,
)
from src.application.interfaces.membership_repository import MembershipRepository
from src.application.interfaces.tenant_repository import TenantRepository
from src.application.interfaces.jwt_service import JwtService
from src.application.services.two_factor_service import (
    TwoFactorService,
)


@dataclass(frozen=True)
class VerifyLoginTwoFactorResponse:
    access_token: str
    refresh_token: str


class VerifyLoginTwoFactor:

    def __init__(
        self,
        user_repository: UserRepository,
        membership_repository: MembershipRepository,
        tenant_repository: TenantRepository,
        two_factor_service: TwoFactorService,
        jwt_service: JwtService,
    ):
        self._user_repository = user_repository
        self._membership_repository = membership_repository
        self._tenant_repository = tenant_repository
        self._two_factor_service = two_factor_service
        self._jwt_service = jwt_service

    def execute(
        self,
        two_factor_token: str,
        code: str,
    ) -> VerifyLoginTwoFactorResponse:

        payload = self._jwt_service.decode_token(
            two_factor_token
        )

        if payload.get("type") != "2fa_pending":
            raise ValueError(
                "Le token 2FA est invalide."
            )

        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")

        if not user_id or not tenant_id:
            raise ValueError(
                "Le token 2FA ne contient pas d utilisateur."
            )

        try:
            user_uuid = UUID(user_id)
            tenant_uuid = UUID(tenant_id)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "L identifiant utilisateur est invalide."
            ) from exc

        user = self._user_repository.find_by_id(
            user_uuid
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        if not user.is_active:
            raise ValueError(
                "Le compte est desactive."
            )

        tenant = self._tenant_repository.find_by_id(tenant_uuid)
        membership = self._membership_repository.find_by_user_and_tenant(user.id, tenant_uuid)
        if tenant is None or not tenant.active or membership is None or not membership.active:
            raise ValueError("Acces tenant refuse.")

        if not user.two_factor_enabled:
            raise ValueError(
                "Le 2FA n est pas active."
            )

        if not user.two_factor_secret:
            raise ValueError(
                "Le secret 2FA est absent."
            )

        if not self._two_factor_service.verify_code(
            secret=user.two_factor_secret,
            code=code,
        ):
            raise ValueError(
                "Code 2FA invalide."
            )

        access_token = self._jwt_service.create_access_token(
            user_id=user.id,
            role=membership.role,
            tenant_id=tenant_uuid,
        )

        refresh_token = self._jwt_service.create_refresh_token(
            user_id=user.id,
            tenant_id=tenant_uuid,
        )

        return VerifyLoginTwoFactorResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

