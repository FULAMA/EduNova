import hashlib
from datetime import datetime, timedelta, timezone

from src.infrastructure.repositories.sqlite_google_nonce_repository import SQLiteGoogleNonceRepository
from src.presentation.api.container import ApplicationContainer


def test_google_nonce_is_stored_as_hash_and_consumed_once():
    container = ApplicationContainer(database_path=":memory:")
    repository = SQLiteGoogleNonceRepository(container._database)
    nonce = "nonce-only-known-to-the-browser"
    nonce_hash = hashlib.sha256(nonce.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    repository.save(nonce_hash, now + timedelta(minutes=5))

    with container._database.connect() as connection:
        row = connection.execute(
            "SELECT nonce_hash FROM google_auth_nonces"
        ).fetchone()
    assert row["nonce_hash"] == nonce_hash
    assert row["nonce_hash"] != nonce
    assert repository.consume(nonce_hash, now) is True
    assert repository.consume(nonce_hash, now) is False


def test_google_nonce_expiration_is_enforced():
    container = ApplicationContainer(database_path=":memory:")
    repository = SQLiteGoogleNonceRepository(container._database)
    now = datetime.now(timezone.utc)
    repository.save("expired-hash", now - timedelta(seconds=1))

    assert repository.consume("expired-hash", now) is False
