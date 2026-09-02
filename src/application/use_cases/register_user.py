from uuid import uuid4

from src.application.interfaces.user_repository import (
    UserRepository,
)
from src.application.services.password_hasher_service import (
    PasswordHasherService,
)
from src.domain.entities.user import User


class RegisterUser:

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherService,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(
        self,
        email: str,
        password: str,
        role: str,
    ) -> User:

        if not email.strip():
            raise ValueError(
                "L email ne peut pas etre vide."
            )

        if not password:
            raise ValueError(
                "Le mot de passe ne peut pas etre vide."
            )

        if not role.strip():
            raise ValueError(
                "Le role ne peut pas etre vide."
            )

        existing_user = self._user_repository.find_by_email(
            email
        )

        if existing_user is not None:
            raise ValueError(
                "Cette adresse email est deja utilisee."
            )

        password_hash = self._password_hasher.hash(
            password
        )

        user = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            role=role,
        )

        self._user_repository.save(user)

        return user
