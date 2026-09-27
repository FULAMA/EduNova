from dataclasses import dataclass

from src.identity.application.interfaces.refresh_token_repository import (
    RefreshTokenRepository,
)
from src.identity.application.interfaces.user_repository import UserRepository
from src.tenancy.application.interfaces.membership_repository import MembershipRepository
from src.tenancy.application.interfaces.tenant_repository import TenantRepository
from src.identity.application.interfaces.jwt_service import JwtService


@dataclass(frozen=True)
class RefreshAccessTokenResponse:
    access_token: str
    refresh_token: str


class RefreshAccessToken:
    def __init__(
        self,
        user_repository: UserRepository,
        membership_repository: MembershipRepository,
        tenant_repository: TenantRepository,
        refresh_token_repository: RefreshTokenRepository,
        jwt_service: JwtService,
    ):
        self._user_repository = user_repository
        self._membership_repository = membership_repository
        self._tenant_repository = tenant_repository
        self._refresh_token_repository = refresh_token_repository
        self._jwt_service = jwt_service

    def execute(
        self,
        refresh_token: str,
    ) -> RefreshAccessTokenResponse:
        payload = self._jwt_service.decode_refresh_token(refresh_token)

        jti = payload["jti"]

        if self._refresh_token_repository.is_revoked(jti):
            raise ValueError("Token refresh revoque.")

        user_id = payload["sub"]
        tenant_id = payload["tenant_id"]

        from uuid import UUID

        try:
            user_uuid = UUID(user_id)
            tenant_uuid = UUID(tenant_id)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "L identifiant utilisateur est invalide."
            ) from exc

        user = self._user_repository.find_by_id(user_uuid)

        if user is None:
            raise ValueError("Utilisateur introuvable.")

        if not user.is_active:
            raise ValueError("Compte desactive.")

        tenant = self._tenant_repository.find_by_id(tenant_uuid)
        if tenant is None or not tenant.active:
            raise ValueError("Tenant inactif ou introuvable.")

        membership = self._membership_repository.find_by_user_and_tenant(user.id, tenant_uuid)
        if membership is None or not membership.active:
            raise ValueError("Le membership n'est pas actif.")

        self._refresh_token_repository.revoke(jti)

        access_token = self._jwt_service.create_access_token(
            user_id=user.id,
            role=membership.role,
            tenant_id=tenant_uuid,
        )

        new_refresh_token = self._jwt_service.create_refresh_token(
            user_id=user.id,
            tenant_id=tenant_uuid,
        )

        return RefreshAccessTokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )

