from uuid import UUID

from src.identity.domain.entities.user import User
from src.identity.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)


DEVELOPMENT_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")
DEVELOPMENT_USER_ID = UUID("00000000-0000-0000-0000-000000000002")
DEVELOPMENT_MEMBERSHIP_ID = UUID("00000000-0000-0000-0000-000000000003")
DEVELOPMENT_USER_EMAIL = "admin@edunova.com"


def seed_development_data(
    database: SQLiteDatabase,
    password: str,
    email: str = DEVELOPMENT_USER_EMAIL,
) -> None:
    user_repository = SQLiteUserRepository(database)
    user_repository.save(
        User(
            id=DEVELOPMENT_USER_ID,
            email=email,
            password_hash=Argon2PasswordHasher().hash(password),
            role="ADMIN",
        )
    )

    with database.connect() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO tenants (id, name, slug, active)
            VALUES (?, ?, ?, ?)
            """,
            (
                str(DEVELOPMENT_TENANT_ID),
                "EduNova Development",
                "edunova-development",
                1,
            ),
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO memberships (
                id, user_id, tenant_id, role, active
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(DEVELOPMENT_MEMBERSHIP_ID),
                str(DEVELOPMENT_USER_ID),
                str(DEVELOPMENT_TENANT_ID),
                "ADMIN",
                1,
            ),
        )
