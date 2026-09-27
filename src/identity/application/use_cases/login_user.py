from dataclasses import dataclass

from src.identity.application.dto.login_user_request import LoginUserRequest
from src.identity.application.interfaces.user_repository import (
    UserRepository,
)
from src.tenancy.application.interfaces.membership_repository import MembershipRepository
from src.tenancy.application.interfaces.tenant_repository import TenantRepository
from src.identity.application.interfaces.jwt_service import JwtService
from src.identity.application.interfaces.password_hasher import PasswordHasher
from src.identity.application.interfaces.two_factor_service import TwoFactorService


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
        membership_repository: MembershipRepository,
        tenant_repository: TenantRepository,
        password_hasher: PasswordHasher,
        two_factor_service: TwoFactorService,
        jwt_service: JwtService,
    ):
        self._user_repository = user_repository
        self._membership_repository = membership_repository
        self._tenant_repository = tenant_repository
        self._password_hasher = password_hasher
        self._two_factor_service = two_factor_service
        self._jwt_service = jwt_service

    def execute(
        self,
        request: LoginUserRequest,
    ) -> LoginUserResponse:

        email = request.email
        password = request.password
        tenant_id = request.tenant_id

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

        tenant = self._tenant_repository.find_by_id(tenant_id)
        membership = self._membership_repository.find_by_user_and_tenant(user.id, tenant_id)
        if tenant is None or not tenant.active or membership is None or not membership.active:
            raise ValueError("Acces tenant refuse.")

        if user.two_factor_enabled:
            two_factor_token = (
                self._jwt_service.create_two_factor_token(
                    user_id=user.id,
                    tenant_id=tenant_id,
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
            role=membership.role,
            tenant_id=tenant_id,
        )

        refresh_token = self._jwt_service.create_refresh_token(
            user_id=user.id,
            tenant_id=tenant_id,
        )

        return LoginUserResponse(
            authenticated=True,
            two_factor_required=False,
            two_factor_token=None,
            access_token=access_token,
            refresh_token=refresh_token,
        )

