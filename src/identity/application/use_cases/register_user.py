from src.identity.application.dto.register_user_request import RegisterUserRequest
from uuid import uuid4

from src.identity.application.dto.register_user_response import (
    RegisterUserResponse,
)
from src.identity.application.interfaces.password_hasher import PasswordHasher
from src.identity.application.interfaces.user_repository import (
    UserRepository,
)
from src.identity.domain.entities.user import User


class RegisterUser:

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(self, request: RegisterUserRequest) -> RegisterUserResponse:
        email = request.email
        password = request.password
        role = request.role

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

        return RegisterUserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            two_factor_enabled=user.two_factor_enabled,
        )
