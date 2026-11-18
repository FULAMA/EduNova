from dataclasses import dataclass
from uuid import UUID

from src.identity.application.dto.login_user_request import LoginUserRequest
from src.identity.application.interfaces.jwt_service import JwtService
from src.identity.application.interfaces.password_hasher import PasswordHasher
from src.identity.application.interfaces.two_factor_service import TwoFactorService
from src.identity.application.interfaces.user_repository import (
    UserRepository,
)
from src.tenancy.application.interfaces.membership_repository import (
    MembershipRepository,
)
from src.tenancy.application.interfaces.tenant_repository import TenantRepository
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant


# Pre-calculated dummy Argon2id hash with standard library parameters.
# Used to equalize verification time when an account does not exist,
# preventing account enumeration via timing analysis.
_DUMMY_ARGON2_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$MlDf/Q70Wop6ClyOiIoGnw$"
    "SGFB3LdEVBFkW6bbruLWXOfoigU/dBkQ7n5zDVX5a1k"
)


@dataclass(frozen=True)
class TenantOptionDto:
    tenant_id: UUID
    tenant_name: str
    tenant_slug: str
    role: str


@dataclass(frozen=True)
class LoginUserResponse:
    authenticated: bool
    two_factor_required: bool
    two_factor_token: str | None
    access_token: str | None
    refresh_token: str | None
    email: str | None = None
    tenant_selection_required: bool = False
    tenant_selection_token: str | None = None
    available_tenants: tuple[TenantOptionDto, ...] = ()


class LoginUser:
    """Authenticates a user against tenant membership and credentials.

    Mitigates timing attacks by computing a dummy password verification when an
    account does not exist. Generic 'Identifiants invalides.' messages are
    returned for non-existent, inactive, and invalid-password accounts alike to
    prevent account enumeration.

    Supports:
    - Explicit tenant_id (backward compatibility).
    - Automatic tenant resolution when tenant_id is omitted:
      * 1 active establishment: automatically resolves tenant and delivers tokens.
      * > 1 active establishments: requires tenant selection and returns a scoped
        temporary selection token without issuing ordinary access tokens.
      * 0 active establishments: rejects access securely.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        membership_repository: MembershipRepository,
        tenant_repository: TenantRepository,
        password_hasher: PasswordHasher,
        two_factor_service: TwoFactorService,
        jwt_service: JwtService,
        dummy_password_hash: str = _DUMMY_ARGON2_HASH,
    ):
        self._user_repository = user_repository
        self._membership_repository = membership_repository
        self._tenant_repository = tenant_repository
        self._password_hasher = password_hasher
        self._two_factor_service = two_factor_service
        self._jwt_service = jwt_service
        self._dummy_password_hash = dummy_password_hash

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
            email.strip().lower()
        )

        if user is None:
            # Timing attack mitigation: run password hasher against dummy hash
            # to approximate the verification time of a real account without
            # revealing account absence.
            self._password_hasher.verify(password, self._dummy_password_hash)
            raise ValueError(
                "Identifiants invalides."
            )

        password_matches = self._password_hasher.verify(
            password,
            user.password_hash,
        )

        # Uniform rejection for wrong password or deactivated accounts
        if not password_matches or not user.is_active:
            raise ValueError(
                "Identifiants invalides."
            )

        # -------------------------------------------------------------
        # Mode 1: Client explicitly supplied tenant_id (backward compat)
        # -------------------------------------------------------------
        if tenant_id is not None:
            tenant = self._tenant_repository.find_by_id(tenant_id)
            membership = self._membership_repository.find_by_user_and_tenant(
                user.id, tenant_id
            )
            if (
                tenant is None
                or not tenant.active
                or membership is None
                or not membership.active
            ):
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
                    email=user.email,
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
                email=user.email,
            )

        # -------------------------------------------------------------
        # Mode 2: Auto-resolution (tenant_id is omitted)
        # -------------------------------------------------------------
        memberships = self._membership_repository.find_by_user(user.id)
        active_options: list[tuple[Membership, Tenant]] = []
        for m in memberships:
            if not m.active:
                continue
            t = self._tenant_repository.find_by_id(m.tenant_id)
            if t is not None and t.active:
                active_options.append((m, t))

        if len(active_options) == 0:
            raise ValueError("Aucun etablissement actif associe a ce compte.")

        if len(active_options) == 1:
            # Mono-tenant: auto-select the unique active establishment
            membership, tenant = active_options[0]

            if user.two_factor_enabled:
                two_factor_token = (
                    self._jwt_service.create_two_factor_token(
                        user_id=user.id,
                        tenant_id=tenant.id,
                    )
                )

                return LoginUserResponse(
                    authenticated=False,
                    two_factor_required=True,
                    two_factor_token=two_factor_token,
                    access_token=None,
                    refresh_token=None,
                    email=user.email,
                )

            access_token = self._jwt_service.create_access_token(
                user_id=user.id,
                role=membership.role,
                tenant_id=tenant.id,
            )

            refresh_token = self._jwt_service.create_refresh_token(
                user_id=user.id,
                tenant_id=tenant.id,
            )

            return LoginUserResponse(
                authenticated=True,
                two_factor_required=False,
                two_factor_token=None,
                access_token=access_token,
                refresh_token=refresh_token,
                email=user.email,
            )

        # Multi-tenant: require establishment selection via temporary token
        selection_token = self._jwt_service.create_tenant_selection_token(user.id)
        available = tuple(
            TenantOptionDto(
                tenant_id=t.id,
                tenant_name=t.name,
                tenant_slug=t.slug,
                role=m.role,
            )
            for m, t in active_options
        )

        return LoginUserResponse(
            authenticated=False,
            two_factor_required=False,
            two_factor_token=None,
            access_token=None,
            refresh_token=None,
            email=user.email,
            tenant_selection_required=True,
            tenant_selection_token=selection_token,
            available_tenants=available,
        )
