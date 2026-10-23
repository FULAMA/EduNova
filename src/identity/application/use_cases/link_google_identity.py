from uuid import UUID, uuid4

from src.identity.application.interfaces.external_identity_repository import (
    ExternalIdentityRepository,
)
from src.identity.application.interfaces.google_identity_verifier import (
    GoogleIdentityVerifier,
)
from src.identity.application.interfaces.user_repository import UserRepository
from src.identity.domain.entities.external_identity import ExternalIdentity


class LinkGoogleIdentity:
    def __init__(
        self,
        user_repository: UserRepository,
        external_identity_repository: ExternalIdentityRepository,
        google_identity_verifier: GoogleIdentityVerifier,
    ):
        self._user_repository = user_repository
        self._external_identity_repository = external_identity_repository
        self._google_identity_verifier = google_identity_verifier

    def execute(self, user_id: UUID, id_token: str) -> ExternalIdentity:
        if not id_token.strip():
            raise ValueError("Le jeton Google ne peut pas etre vide.")

        identity = self._google_identity_verifier.verify(id_token)
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
