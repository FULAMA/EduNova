from dataclasses import dataclass
from uuid import UUID

from src.application.interfaces.user_repository import (
    UserRepository,
)
from src.application.services.jwt_service import JwtService
from src.application.services.password_hasher_service import (
    PasswordHasherService,
)
from src.application.services.two_factor_service import (
    TwoFactorService,
)


@dataclass(frozen=True)
class LoginUserResponse:
    authenticated: bool
    two_factor_required: bool
    two_factor_token: str | None
    access_token: str | None
    refresh_token: str | None


class LoginUser:

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherService,
        two_factor_service: TwoFactorService,
        jwt_service: JwtService,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._two_factor_service = two_factor_service
        self._jwt_service = jwt_service

    def execute(
        self,
        email: str,
        password: str,
    ) -> LoginUserResponse:

        if not email.strip():
            raise ValueError(
                "L email ne peut pas etre vide."
            )

        if not password:
            raise ValueError(
                "Le mot de passe ne peut pas etre vide."
            )

        user = self._user_repository.find_by_email(
            email
        )

        if user is None:
            raise ValueError(
                "Identifiants invalides."
            )

        if not user.is_active:
            raise ValueError(
                "Le compte est desactive."
            )

        if not self._password_hasher.verify(
            password,
            user.password_hash,
        ):
            raise ValueError(
                "Identifiants invalides."
            )

        if user.two_factor_enabled:
            two_factor_token = (
                self._jwt_service.create_two_factor_token(
                    user_id=user.id,
                )
            )

            return LoginUserResponse(
                authenticated=False,
                two_factor_required=True,
                two_factor_token=two_factor_token,
                access_token=None,
                refresh_token=None,
            )

        access_token = self._jwt_service.create_access_token(
            user_id=user.id,
            role=user.role,
        )

        refresh_token = self._jwt_service.create_refresh_token(
            user_id=user.id,
        )

        return LoginUserResponse(
            authenticated=True,
            two_factor_required=False,
            two_factor_token=None,
            access_token=access_token,
            refresh_token=refresh_token,
        )
