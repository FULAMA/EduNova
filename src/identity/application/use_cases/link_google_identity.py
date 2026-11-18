import hashlib
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.identity.application.interfaces.external_identity_repository import (
    ExternalIdentityRepository,
)
from src.identity.application.interfaces.google_identity_verifier import (
    GoogleIdentityVerifier,
)
from src.identity.application.interfaces.google_nonce_repository import GoogleNonceRepository
from src.identity.application.interfaces.password_hasher import PasswordHasher
from src.identity.application.interfaces.totp_anti_replay_repository import TotpAntiReplayRepository
from src.identity.application.interfaces.two_factor_service import TwoFactorService
from src.identity.application.interfaces.user_repository import UserRepository
from src.identity.domain.entities.external_identity import ExternalIdentity


class LinkGoogleIdentity:
    def __init__(
        self,
        user_repository: UserRepository,
        external_identity_repository: ExternalIdentityRepository,
        google_identity_verifier: GoogleIdentityVerifier,
        password_hasher: PasswordHasher,
        two_factor_service: TwoFactorService,
        totp_anti_replay_repository: TotpAntiReplayRepository,
        google_nonce_repository: GoogleNonceRepository,
    ):
        self._user_repository = user_repository
        self._external_identity_repository = external_identity_repository
        self._google_identity_verifier = google_identity_verifier
        self._password_hasher = password_hasher
        self._two_factor_service = two_factor_service
        self._totp_anti_replay_repository = totp_anti_replay_repository
        self._google_nonce_repository = google_nonce_repository

    def execute(
        self,
        user_id: UUID,
        id_token: str,
        nonce: str,
        password: str,
        totp_code: str | None = None,
    ) -> ExternalIdentity:
        if not id_token.strip():
            raise ValueError("Le jeton Google ne peut pas etre vide.")

        user = self._user_repository.find_by_id(user_id)
        if (
            user is None
            or not user.is_active
            or not password
            or not self._password_hasher.verify(password, user.password_hash)
        ):
            raise ValueError("Reauthentification EduNova refusee.")

        if user.two_factor_enabled:
            if not user.two_factor_secret or not totp_code:
                raise ValueError("Reauthentification EduNova refusee.")
            if not self._two_factor_service.verify_code(
                user.two_factor_secret, totp_code
            ):
                raise ValueError("Reauthentification EduNova refusee.")
            interval = int(datetime.now(timezone.utc).timestamp()) // 30
            try:
                accepted = self._totp_anti_replay_repository.record_interval(
                    user_id, interval
                )
            except Exception as exc:
                raise ValueError("Reauthentification EduNova refusee.") from exc
            if not accepted:
                raise ValueError("Reauthentification EduNova refusee.")

        if not nonce.strip():
            raise ValueError("Nonce Google invalide.")
        nonce_hash = hashlib.sha256(nonce.encode("utf-8")).hexdigest()
        if not self._google_nonce_repository.consume(
            nonce_hash, datetime.now(timezone.utc)
        ):
            raise ValueError("Nonce Google invalide.")

        identity = self._google_identity_verifier.verify(id_token, nonce)
        if (
            not identity.subject
            or not identity.email.strip()
            or not identity.email_verified
        ):
            raise ValueError("Identite Google refusee.")

        existing = self._external_identity_repository.find_by_provider_and_subject(
            "google",
            identity.subject,
        )
        if existing is not None:
            if existing.user_id == user_id:
                return existing
            raise ValueError("Identite Google deja liee.")

        linked_for_user = self._external_identity_repository.find_by_user_and_provider(
            user_id,
            "google",
        )
        if linked_for_user is not None:
            raise ValueError("Une identite Google est deja liee.")

        email_owner = self._user_repository.find_by_email(identity.email)
        if email_owner is not None and email_owner.id != user_id:
            raise ValueError("Identite Google refusee.")

        return self._external_identity_repository.link(
            ExternalIdentity(
                id=uuid4(),
                provider="google",
                subject=identity.subject,
                user_id=user_id,
            )
        )
