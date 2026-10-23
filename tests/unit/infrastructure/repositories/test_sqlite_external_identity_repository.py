from uuid import uuid4

import pytest

from src.identity.domain.entities.external_identity import ExternalIdentity
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_external_identity_repository import (
    SQLiteExternalIdentityRepository,
)
from src.identity.domain.entities.user import User
from src.infrastructure.repositories.sqlite_user_repository import SQLiteUserRepository


def test_external_identity_persists_and_is_unique():
    database = SQLiteDatabase(":memory:")
    database.initialize()
    user = User(uuid4(), "user@example.test", "hash", "ADMIN")
    SQLiteUserRepository(database).save(user)
    repository = SQLiteExternalIdentityRepository(database)
    identity = ExternalIdentity(uuid4(), "google", "opaque-subject", user.id)

    assert repository.link(identity) == identity
    assert repository.find_by_provider_and_subject(
        "google",
        "opaque-subject",
    ) == identity
    assert repository.find_by_user_and_provider(user.id, "google") == identity

    with pytest.raises(ValueError, match="deja liee"):
        repository.link(ExternalIdentity(uuid4(), "google", "opaque-subject", uuid4()))


def test_external_identity_provider_subject_is_opaque():
    database = SQLiteDatabase(":memory:")
    database.initialize()
    user = User(uuid4(), "user@example.test", "hash", "ADMIN")
    SQLiteUserRepository(database).save(user)
    repository = SQLiteExternalIdentityRepository(database)
    subject = "CaseSensitive/Sub:opaque"
    identity = ExternalIdentity(uuid4(), "google", subject, user.id)

    repository.link(identity)

    assert repository.find_by_provider_and_subject("google", subject) == identity
