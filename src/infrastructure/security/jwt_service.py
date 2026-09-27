from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt

from src.identity.application.interfaces.jwt_service import JwtService as JwtServiceInterface


class JwtService(JwtServiceInterface):
    def __init__(
        self,
        secret_key: str,
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ):
        if not secret_key.strip():
            raise ValueError("La cle JWT ne peut pas etre vide.")

        if len(secret_key) < 32:
            raise ValueError(
                "La cle JWT doit contenir au moins 32 caracteres."
            )

        if access_token_expire_minutes <= 0:
            raise ValueError(
                "La duree du token access doit etre superieure a zero."
            )

        if refresh_token_expire_days <= 0:
            raise ValueError(
                "La duree du token refresh doit etre superieure a zero."
            )

        self._secret_key = secret_key
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(self, user_id: UUID, role: str, tenant_id: UUID) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "role": role,
            "tenant_id": str(tenant_id),
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self._access_token_expire_minutes),
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm="HS256",
        )

    def create_refresh_token(self, user_id: UUID, tenant_id: UUID) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "tenant_id": str(tenant_id),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=self._refresh_token_expire_days),
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm="HS256",
        )

    def create_two_factor_token(self, user_id: UUID, tenant_id: UUID) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "type": "2fa_pending",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm="HS256",
        )

    def decode_token(self, token: str) -> dict:
        if not token:
            raise ValueError("Le token ne peut pas etre vide.")

        try:
            return jwt.decode(
                token,
                self._secret_key,
                algorithms=["HS256"],
            )
        except jwt.PyJWTError as exc:
            raise ValueError("Token JWT invalide.") from exc

    def decode_refresh_token(self, token: str) -> dict:
        payload = self.decode_token(token)

        if payload.get("type") != "refresh":
            raise ValueError("Token refresh requis.")

        if not payload.get("sub"):
            raise ValueError(
                "Le token refresh ne contient pas d utilisateur."
            )

        if not payload.get("jti"):
            raise ValueError(
                "Le token refresh ne contient pas de jti."
            )

        if not payload.get("tenant_id"):
            raise ValueError("Le token refresh ne contient pas de tenant.")

        return payload


