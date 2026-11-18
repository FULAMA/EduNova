from src.identity.application.interfaces.jwt_service import JwtService
from src.identity.application.interfaces.refresh_token_repository import (
    RefreshTokenRepository,
)


class LogoutUser:
    """Revokes the presented refresh token jti (idempotent).

    Access tokens are not blacklisted: they remain valid until natural
    expiry, consistent with the existing JWT architecture.
    """

    def __init__(
        self,
        refresh_token_repository: RefreshTokenRepository,
        jwt_service: JwtService,
    ):
        self._refresh_token_repository = refresh_token_repository
        self._jwt_service = jwt_service

    def execute(self, refresh_token: str) -> None:
        if not refresh_token or not refresh_token.strip():
            raise ValueError("Token refresh requis.")

        payload = self._jwt_service.decode_refresh_token(refresh_token.strip())
        jti = payload["jti"]
        if not isinstance(jti, str) or not jti.strip():
            raise ValueError("Token refresh invalide.")

        self._refresh_token_repository.revoke(jti)
