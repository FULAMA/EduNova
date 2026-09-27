from uuid import uuid4


from src.identity.domain.entities.user import User
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)


def create_database():
    database = SQLiteDatabase(":memory:")
    database.initialize()
    return database


def test_save_and_find_user_by_id():
    database = create_database()
    repository = SQLiteUserRepository(database)

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    repository.save(user)

    result = repository.find_by_id(user.id)

    assert result is not None
    assert result.id == user.id
    assert result.email == user.email
    assert result.password_hash == user.password_hash
    assert result.role == user.role
    assert result.is_active is True
    assert result.two_factor_enabled is False
    assert result.two_factor_secret is None


def test_find_user_by_email():
    database = create_database()
    repository = SQLiteUserRepository(database)

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
    )

    repository.save(user)

    result = repository.find_by_email("admin@edunova.com")

    assert result is not None
    assert result.id == user.id


def test_find_unknown_user_returns_none():
    database = create_database()
    repository = SQLiteUserRepository(database)

    assert repository.find_by_id(uuid4()) is None


def test_find_unknown_email_returns_none():
    database = create_database()
    repository = SQLiteUserRepository(database)

    assert repository.find_by_email("unknown@edunova.com") is None
