from google.auth.transport import requests
from google.oauth2 import id_token

from src.identity.application.interfaces.google_identity_verifier import (
    GoogleIdentity,
    GoogleIdentityVerifier,
)


class GoogleIdTokenVerifier(GoogleIdentityVerifier):
    def __init__(self, client_id: str | None):
        self._client_id = client_id

    def verify(self, id_token_value: str) -> GoogleIdentity:
        if not self._client_id:
            raise ValueError("Google auth non configuree.")

        try:
            claims = id_token.verify_oauth2_token(
                id_token_value,
                requests.Request(),
                self._client_id,
            )
        except (ValueError, TypeError, RuntimeError) as exc:
            raise ValueError("Jeton Google invalide.") from exc

        issuer = claims.get("iss")
        email = claims.get("email")
        subject = claims.get("sub")
        if (
            issuer not in {"accounts.google.com", "https://accounts.google.com"}
            or not isinstance(subject, str)
            or not subject
            or not isinstance(email, str)
        ):
            raise ValueError("Jeton Google invalide.")

        return GoogleIdentity(
            subject=subject,
            email=email,
            email_verified=claims.get("email_verified") is True,
        )
