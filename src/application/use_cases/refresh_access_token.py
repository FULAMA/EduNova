from dataclasses import dataclass

from src.application.interfaces.refresh_token_repository import (
    RefreshTokenRepository,
)
from src.application.interfaces.user_repository import UserRepository
from src.application.services.jwt_service import JwtService


@dataclass(frozen=True)
class RefreshAccessTokenResponse:
    access_token: str
    refresh_token: str


class RefreshAccessToken:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        jwt_service: JwtService,
    ):
        self._user_repository = user_repository
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

        from uuid import UUID

        try:
            user_uuid = UUID(user_id)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "L identifiant utilisateur est invalide."
            ) from exc

        user = self._user_repository.find_by_id(user_uuid)

        if user is None:
            raise ValueError("Utilisateur introuvable.")

        if not user.is_active:
            raise ValueError("Compte desactive.")

        self._refresh_token_repository.revoke(jti)

        access_token = self._jwt_service.create_access_token(
            user_id=user.id,
            role=user.role,
        )

        new_refresh_token = self._jwt_service.create_refresh_token(
            user_id=user.id,
        )

        return RefreshAccessTokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
        )
