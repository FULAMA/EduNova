from uuid import uuid4

from src.domain.entities.user import User
from src.presentation.api.dependencies.auth import (
    get_current_user,
    get_optional_current_user,
)


def authenticate_as(app, role: str = "ADMIN") -> User:
    """Simule un utilisateur authentifie pour les tests HTTP."""

    user = User(
        id=uuid4(),
        email=f"{role.lower()}@edunova.com",
        password_hash="hashed-password",
        role=role,
    )

    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_optional_current_user] = lambda: user

    return user
