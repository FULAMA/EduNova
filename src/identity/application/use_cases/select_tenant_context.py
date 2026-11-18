import hashlib
from uuid import UUID

from src.identity.application.dto.select_tenant_context_request import (
    SelectTenantContextRequest,
)
from src.identity.application.interfaces.consumed_token_repository import (
    ConsumedTokenRepository,
)
from src.identity.application.interfaces.jwt_service import JwtService
from src.identity.application.interfaces.rate_limiter import RateLimiter
from src.identity.application.interfaces.user_repository import (
    UserRepository,
)
from src.identity.application.use_cases.login_user import LoginUserResponse
from src.tenancy.application.interfaces.membership_repository import (
    MembershipRepository,
)
from src.tenancy.application.interfaces.tenant_repository import TenantRepository


class SelectTenantContext:
    """Consumes a temporary tenant selection token to finalize login into a chosen establishment.

    Guarantees:
    - Persistent replay protection: the selection token can only be consumed once,
      enforced atomically in database (survives restarts and multi-worker setups).
    - Expiration & integrity check: invalid, expired, or wrong-type tokens are rejected.
    - Server-side authorization check: verifies the user belongs to the requested tenant
      and both membership and tenant are active.
    - Emits access and refresh tokens (or initiates 2FA pending session if enabled).
    """

    def __init__(
        self,
        user_repository: UserRepository,
        membership_repository: MembershipRepository,
        tenant_repository: TenantRepository,
        jwt_service: JwtService,
        rate_limiter: RateLimiter | None = None,
        consumed_token_repository: ConsumedTokenRepository | None = None,
    ):
        self._user_repository = user_repository
        self._membership_repository = membership_repository
        self._tenant_repository = tenant_repository
        self._jwt_service = jwt_service
        self._rate_limiter = rate_limiter
        self._consumed_token_repository = consumed_token_repository

    def execute(
        self,
        request: SelectTenantContextRequest,
    ) -> LoginUserResponse:
        token = request.tenant_selection_token
        tenant_id = request.tenant_id

        if not token or not token.strip():
            raise ValueError("Le jeton de selection ne peut pas etre vide.")

        try:
            payload = self._jwt_service.decode_token(token)
        except Exception as exc:
            raise ValueError("Le jeton de selection est invalide ou expire.") from exc

        if payload.get("type") != "tenant_selection":
            raise ValueError("Le jeton de selection est invalide.")

        token_id = payload.get("jti") or hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

        # Atomic anti-replay check
        if self._consumed_token_repository is not None:
            if not self._consumed_token_repository.consume(token_id):
                raise ValueError("Jeton de selection deja consomme.")
        elif self._rate_limiter is not None:
            if self._rate_limiter.is_limited(
                f"tenant_selection:consumed:{token_id}", limit=1, window_seconds=600
            ):
                raise ValueError("Jeton de selection deja consomme.")
            self._rate_limiter.check_and_record(
                f"tenant_selection:consumed:{token_id}", limit=1, window_seconds=600
            )

        raw_sub = payload.get("sub")
        if not raw_sub:
            raise ValueError("Le jeton ne contient pas d identifiant utilisateur.")

        try:
            user_id = UUID(raw_sub)
        except (ValueError, TypeError) as exc:
            raise ValueError("Identifiant utilisateur invalide dans le jeton.") from exc

        user = self._user_repository.find_by_id(user_id)
        if user is None or not user.is_active:
            raise ValueError("Compte utilisateur introuvable ou desactive.")

        # Server-side authorization check
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

        # Handle 2FA if enabled
        if user.two_factor_enabled:
            two_factor_token = self._jwt_service.create_two_factor_token(
                user_id=user.id,
                tenant_id=tenant_id,
            )

            return LoginUserResponse(
                authenticated=False,
                two_factor_required=True,
                two_factor_token=two_factor_token,
                access_token=None,
                refresh_token=None,
                email=user.email,
            )

        # Issue standard session tokens
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
