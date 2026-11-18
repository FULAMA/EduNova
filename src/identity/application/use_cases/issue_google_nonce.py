import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from src.identity.application.interfaces.google_nonce_repository import GoogleNonceRepository


class IssueGoogleNonce:
    def __init__(self, repository: GoogleNonceRepository):
        self._repository = repository

    def execute(self) -> str:
        nonce = secrets.token_urlsafe(32)
        nonce_hash = hashlib.sha256(nonce.encode("utf-8")).hexdigest()
        self._repository.save(
            nonce_hash,
            datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        return nonce
