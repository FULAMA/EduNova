import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from src.identity.application.dto.verify_login_two_factor_request import (
    VerifyLoginTwoFactorRequest,
)
from src.identity.application.interfaces.jwt_service import JwtService
from src.identity.application.interfaces.rate_limiter import RateLimiter
from src.identity.application.interfaces.totp_anti_replay_repository import (
    TotpAntiReplayRepository,
)
from src.identity.application.interfaces.two_factor_service import TwoFactorService
from src.identity.application.interfaces.user_repository import (
    UserRepository,
)
from src.tenancy.application.interfaces.membership_repository import (
    MembershipRepository,
)
from src.tenancy.application.interfaces.tenant_repository import TenantRepository


# TOTP default interval in seconds (pyotp default)
_TOTP_INTERVAL_SECONDS = 30


@dataclass(frozen=True)
class VerifyLoginTwoFactorResponse:
    access_token: str
    refresh_token: str


class VerifyLoginTwoFactor:
    """Verifies a pending 2FA authentication session with a TOTP code.

    Enforces:
    - Persistent TOTP anti-replay via TotpAntiReplayRepository (survives restarts)
    - Brute-force protection via RateLimiter (in-memory, per-session)
    - Strict limit of 3 attempts per pending 2FA token session
    - Atomic interval recording to prevent concurrent replay
    """

    def __init__(
        self,
        user_repository: UserRepository,
        membership_repository: MembershipRepository,
        tenant_repository: TenantRepository,
        two_factor_service: TwoFactorService,
        jwt_service: JwtService,
        rate_limiter: RateLimiter | None = None,
        totp_anti_replay_repository: TotpAntiReplayRepository | None = None,
        time_provider: Callable[[], float] | None = None,
    ):
        self._user_repository = user_repository
        self._membership_repository = membership_repository
        self._tenant_repository = tenant_repository
        self._two_factor_service = two_factor_service
        self._jwt_service = jwt_service
        self._rate_limiter = rate_limiter
        self._totp_anti_replay_repository = totp_anti_replay_repository
        self._time_provider = time_provider or time.time

    def _get_totp_interval(self) -> int:
        """Calculate current TOTP time interval index."""
        return int(self._time_provider()) // _TOTP_INTERVAL_SECONDS

    def execute(
        self,
        request: VerifyLoginTwoFactorRequest,
    ) -> VerifyLoginTwoFactorResponse:

        two_factor_token = request.two_factor_token
        code = request.code

        payload = self._jwt_service.decode_token(
            two_factor_token
        )

        if payload.get("type") != "2fa_pending":
            raise ValueError(
                "Le token 2FA est invalide."
            )

        token_id = payload.get("jti") or hashlib.sha256(
            two_factor_token.encode("utf-8")
        ).hexdigest()

        # Brute-force protection via rate limiter (in-memory, per token session)
        if self._rate_limiter is not None:
            if self._rate_limiter.is_limited(
                f"2fa:consumed:{token_id}", limit=1, window_seconds=600
            ):
                raise ValueError("Token 2FA deja consomme.")

            # Limit attempts per 2FA pending session
            attempt_result = self._rate_limiter.check_and_record(
                key=f"2fa:attempts:{token_id}",
                limit=3,
                window_seconds=300,
            )
            if not attempt_result.allowed:
                raise ValueError(
                    "Nombre maximal de tentatives 2FA depasse."
                )

        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")

        if not user_id or not tenant_id:
            raise ValueError(
                "Le token 2FA ne contient pas d utilisateur."
            )

        try:
            user_uuid = UUID(user_id)
            tenant_uuid = UUID(tenant_id)
        except (ValueError, TypeError) as exc:
            raise ValueError(
                "L identifiant utilisateur est invalide."
            ) from exc

        user = self._user_repository.find_by_id(
            user_uuid
        )

        if user is None:
            raise ValueError(
                "Utilisateur introuvable."
            )

        if not user.is_active:
            raise ValueError(
                "Le compte est desactive."
            )

        tenant = self._tenant_repository.find_by_id(tenant_uuid)
        membership = self._membership_repository.find_by_user_and_tenant(
            user.id, tenant_uuid
        )
        if (
            tenant is None
            or not tenant.active
            or membership is None
            or not membership.active
        ):
            raise ValueError("Acces tenant refuse.")

        if not user.two_factor_enabled:
            raise ValueError(
                "Le 2FA n est pas active."
            )

        if not user.two_factor_secret:
            raise ValueError(
                "Le secret 2FA est absent."
            )

        # Verify the TOTP code
        if not self._two_factor_service.verify_code(
            secret=user.two_factor_secret,
            code=code,
        ):
            raise ValueError(
                "Code 2FA invalide."
            )

        # Persistent anti-replay: record the TOTP interval
        # This prevents the same TOTP code from being used twice,
        # even across server restarts or multiple processes.
        current_interval = self._get_totp_interval()
        if self._totp_anti_replay_repository is not None:
            try:
                recorded = self._totp_anti_replay_repository.record_interval(
                    user_id=user_uuid,
                    interval_index=current_interval,
                )
            except Exception as exc:
                raise ValueError("Code 2FA deja utilise.") from exc

            if not recorded:
                raise ValueError("Code 2FA deja utilise.")

        if self._rate_limiter is not None:
            self._rate_limiter.check_and_record(
                key=f"2fa:consumed:{token_id}",
                limit=1,
                window_seconds=600,
            )

        access_token = self._jwt_service.create_access_token(
            user_id=user.id,
            role=membership.role,
            tenant_id=tenant_uuid,
        )

        refresh_token = self._jwt_service.create_refresh_token(
            user_id=user.id,
            tenant_id=tenant_uuid,
        )

        return VerifyLoginTwoFactorResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
