from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt


class JwtService:
    def __init__(
        self,
        secret_key: str,
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ):
        if not secret_key.strip():
            raise ValueError("La cle JWT ne peut pas etre vide.")

        self._secret_key = secret_key
        self._access_token_expire_minutes = access_token_expire_minutes
        self._refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(self, user_id: UUID, role: str) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(
                minutes=self._access_token_expire_minutes
            ),
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm="HS256",
        )

    def create_refresh_token(self, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "jti": str(uuid4()),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(
                days=self._refresh_token_expire_days
            ),
        }

        return jwt.encode(
            payload,
            self._secret_key,
            algorithm="HS256",
        )

    def create_two_factor_token(self, user_id: UUID) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
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

        return payload
