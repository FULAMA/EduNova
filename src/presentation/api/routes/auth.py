from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.identity.application.use_cases.enable_two_factor import EnableTwoFactor
from src.identity.application.use_cases.login_user import LoginUser
from src.identity.application.use_cases.login_with_google import LoginWithGoogle
from src.identity.application.use_cases.link_google_identity import LinkGoogleIdentity
from src.identity.application.use_cases.logout_user import LogoutUser
from src.identity.application.use_cases.refresh_access_token import RefreshAccessToken
from src.identity.application.dto.register_user_request import RegisterUserRequest as ApplicationRegisterUserRequest
from src.identity.application.dto.login_user_request import LoginUserRequest as ApplicationLoginUserRequest
from src.identity.application.dto.google_login_request import GoogleLoginRequest as ApplicationGoogleLoginRequest
from src.identity.application.dto.verify_login_two_factor_request import VerifyLoginTwoFactorRequest as ApplicationVerifyLoginTwoFactorRequest
from src.identity.application.use_cases.register_user import RegisterUser
from src.identity.application.dto.register_establishment_request import (
    RegisterEstablishmentRequest as ApplicationRegisterEstablishmentRequest,
)
from src.identity.application.dto.select_tenant_context_request import (
    SelectTenantContextRequest as ApplicationSelectTenantContextRequest,
)
from src.identity.application.use_cases.register_establishment import RegisterEstablishment
from src.identity.application.use_cases.select_tenant_context import SelectTenantContext
from src.presentation.api.schemas.register_establishment_request import (
    RegisterEstablishmentRequest,
)
from src.presentation.api.schemas.register_establishment_response import (
    RegisterEstablishmentResponse,
)
from src.presentation.api.schemas.select_tenant_request import (
    SelectTenantRequest,
)
from src.presentation.api.schemas.login_user_response import TenantOptionSchema

from src.identity.application.use_cases.verify_login_two_factor import VerifyLoginTwoFactor
from src.identity.application.use_cases.verify_two_factor import VerifyTwoFactor

from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.identity.application.interfaces.rate_limiter import RateLimiter

from src.presentation.api.dependencies.auth import (
    get_current_user,
    get_tenant_context,
    require_role,
)

from src.presentation.api.dependencies import (
    get_enable_two_factor_use_case,
    get_login_user_use_case,
    get_login_with_google_use_case,
    get_link_google_identity_use_case,
    get_issue_google_nonce_use_case,
    get_membership_repository,
    get_logout_user_use_case,
    get_refresh_access_token_use_case,
    get_register_user_use_case,
    get_register_establishment_use_case,
    get_select_tenant_context_use_case,
    get_verify_login_two_factor_use_case,
    get_verify_two_factor_use_case,
    get_rate_limiter,
)
from src.shared.application.context.tenant_context import TenantContext
from src.tenancy.application.interfaces.membership_repository import (
    MembershipRepository,
)

from src.presentation.api.schemas.enable_two_factor_response import (
    EnableTwoFactorResponse,
)
from src.presentation.api.schemas.me_response import MeResponse
from src.presentation.api.schemas.login_user_request import LoginUserRequest
from src.presentation.api.schemas.google_login_request import GoogleLoginRequest
from src.presentation.api.schemas.google_link_request import GoogleLinkRequest
from src.presentation.api.schemas.google_link_response import GoogleLinkResponse
from src.presentation.api.schemas.google_nonce_response import GoogleNonceResponse
from src.identity.application.use_cases.issue_google_nonce import IssueGoogleNonce
from src.presentation.api.schemas.login_user_response import LoginUserResponse
from src.presentation.api.schemas.refresh_token_request import (
    RefreshTokenRequest,
)
from src.presentation.api.schemas.register_user_request import RegisterUserRequest
from src.presentation.api.schemas.register_user_response import RegisterUserResponse
from src.presentation.api.schemas.verify_login_two_factor_request import (
    VerifyLoginTwoFactorRequest,
)
from src.presentation.api.schemas.verify_login_two_factor_response import (
    VerifyLoginTwoFactorResponse,
)
from src.presentation.api.schemas.verify_two_factor_request import (
    VerifyTwoFactorRequest,
)
from src.presentation.api.schemas.verify_two_factor_response import (
    VerifyTwoFactorResponse,
)

_TRUSTED_PROXIES = {"127.0.0.1", "::1", "localhost", "testclient"}


def get_client_ip(request: Request, trusted_proxies: set[str] = _TRUSTED_PROXIES) -> str:
    client_host = request.client.host if request.client else "127.0.0.1"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded and client_host in trusted_proxies:
        return forwarded.split(",")[0].strip()
    return client_host


router = APIRouter()


@router.post(
    "/auth/register-establishment",
    response_model=RegisterEstablishmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_establishment(
    request: RegisterEstablishmentRequest,
    http_request: Request,
    use_case: RegisterEstablishment = Depends(get_register_establishment_use_case),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    client_ip = get_client_ip(http_request)
    ip_result = rate_limiter.check_and_record(
        key=f"register_establishment:ip:{client_ip}",
        limit=5,
        window_seconds=900,
    )
    if not ip_result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives d inscription. Veuillez reessayer plus tard.",
            headers={"Retry-After": str(ip_result.retry_after)},
        )

    try:
        application_request = ApplicationRegisterEstablishmentRequest(
            school_name=request.school_name,
            admin_name=request.admin_name,
            email=request.email,
            password=request.password,
        )
        result = use_case.execute(application_request)

        return RegisterEstablishmentResponse(
            tenant_id=result.tenant_id,
            tenant_name=result.tenant_name,
            tenant_slug=result.tenant_slug,
            user_id=result.user_id,
            admin_name=result.admin_name,
            email=result.email,
            role=result.role,
        )

    except ValueError as exc:
        if str(exc) == "Cette adresse email est deja utilisee.":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/auth/register",
    response_model=RegisterUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: RegisterUserRequest,
    http_request: Request,
    use_case: RegisterUser = Depends(get_register_user_use_case),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    client_ip = get_client_ip(http_request)
    ip_result = rate_limiter.check_and_record(
        key=f"register:ip:{client_ip}",
        limit=5,
        window_seconds=60,
    )
    if not ip_result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives d inscription. Veuillez reessayer plus tard.",
            headers={"Retry-After": str(ip_result.retry_after)},
        )

    try:
        application_request = ApplicationRegisterUserRequest(
            email=request.email,
            password=request.password,
            # Public registration must never choose a privileged role.
            # Administrative roles are provisioned through controlled
            # back-office/bootstrap workflows only.
            role="STUDENT",
        )
        user = use_case.execute(application_request)

        return RegisterUserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            two_factor_enabled=user.two_factor_enabled,
        )

    except ValueError as exc:
        if str(exc) in {
            "Identifiants invalides.",
            "Le compte est desactive.",
        }:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            )

        if str(exc) in {
            "Acces tenant refuse.",
            "Aucun etablissement actif associe a ce compte.",
        }:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/auth/login",
    response_model=LoginUserResponse,
)
def login_user(
    request: LoginUserRequest,
    http_request: Request,
    use_case: LoginUser = Depends(get_login_user_use_case),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    client_ip = get_client_ip(http_request)
    normalized_email = request.email.strip().lower()

    # 1. Per-IP general throttle (protects against distributed credential stuffing / DoS)
    ip_result = rate_limiter.check_and_record(
        key=f"login:ip:{client_ip}",
        limit=15,
        window_seconds=60,
    )
    if not ip_result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives de connexion. Veuillez reessayer plus tard.",
            headers={"Retry-After": str(ip_result.retry_after)},
        )

    # 2. Per-(IP, Account) targeted throttle (prevents brute-force on victim account from this IP)
    target_key = f"login:target:{client_ip}:{normalized_email}"
    target_result = rate_limiter.check_and_record(
        key=target_key,
        limit=5,
        window_seconds=60,
    )
    if not target_result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives pour ce compte. Veuillez reessayer plus tard.",
            headers={"Retry-After": str(target_result.retry_after)},
        )

    try:
        application_request = ApplicationLoginUserRequest(
            email=request.email,
            password=request.password,
            tenant_id=request.tenant_id,
        )
        result = use_case.execute(application_request)

        # Successful authentication clears the failed attempt count for this client & account
        rate_limiter.reset(target_key)

        available = [
            TenantOptionSchema(
                tenant_id=t.tenant_id,
                tenant_name=t.tenant_name,
                tenant_slug=t.tenant_slug,
                role=t.role,
            )
            for t in result.available_tenants
        ]

        return LoginUserResponse(
            authenticated=result.authenticated,
            two_factor_required=result.two_factor_required,
            two_factor_token=result.two_factor_token,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            email=result.email,
            tenant_selection_required=result.tenant_selection_required,
            tenant_selection_token=result.tenant_selection_token,
            available_tenants=available,
        )

    except ValueError as exc:
        if str(exc) in {
            "Identifiants invalides.",
            "Le compte est desactive.",
        }:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            )

        if str(exc) == "Acces tenant refuse.":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acces tenant refuse.",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/auth/select-tenant",
    response_model=LoginUserResponse,
)
def select_tenant(
    request: SelectTenantRequest,
    http_request: Request,
    use_case: SelectTenantContext = Depends(get_select_tenant_context_use_case),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    client_ip = get_client_ip(http_request)

    ip_result = rate_limiter.check_and_record(
        key=f"select_tenant:ip:{client_ip}",
        limit=10,
        window_seconds=60,
    )
    if not ip_result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives de selection. Veuillez reessayer plus tard.",
            headers={"Retry-After": str(ip_result.retry_after)},
        )

    try:
        app_request = ApplicationSelectTenantContextRequest(
            tenant_selection_token=request.tenant_selection_token,
            tenant_id=request.tenant_id,
        )
        result = use_case.execute(app_request)

        return LoginUserResponse(
            authenticated=result.authenticated,
            two_factor_required=result.two_factor_required,
            two_factor_token=result.two_factor_token,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            email=result.email,
            tenant_selection_required=result.tenant_selection_required,
            tenant_selection_token=result.tenant_selection_token,
        )

    except ValueError as exc:
        err_msg = str(exc)
        if err_msg == "Jeton de selection deja consomme.":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=err_msg,
            )
        if err_msg == "Acces tenant refuse.":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=err_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg,
        )


@router.post(
    "/auth/google/nonce",
    response_model=GoogleNonceResponse,
)
def issue_google_nonce(
    http_request: Request,
    use_case: IssueGoogleNonce = Depends(get_issue_google_nonce_use_case),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    client_ip = get_client_ip(http_request)
    result = rate_limiter.check_and_record(
        key=f"google_nonce:ip:{client_ip}", limit=30, window_seconds=60
    )
    if not result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives de connexion Google.",
            headers={"Retry-After": str(result.retry_after)},
        )
    return GoogleNonceResponse(nonce=use_case.execute())


@router.post(
    "/auth/google",
    response_model=LoginUserResponse,
)
def login_with_google(
    request: GoogleLoginRequest,
    use_case: LoginWithGoogle = Depends(get_login_with_google_use_case),
):
    try:
        result = use_case.execute(
            ApplicationGoogleLoginRequest(
                id_token=request.id_token,
                tenant_id=request.tenant_id,
                nonce=request.nonce,
            )
        )

        return LoginUserResponse(
            authenticated=result.authenticated,
            two_factor_required=result.two_factor_required,
            two_factor_token=result.two_factor_token,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            email=result.email,
        )
    except ValueError as exc:
        if str(exc) in {
            "Identifiants invalides.",
            "Le compte est desactive.",
            "Jeton Google invalide.",
            "Nonce Google invalide.",
            "L adresse e-mail Google n est pas verifiee.",
        }:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentification Google refusee.",
            ) from exc

        if str(exc) == "Acces tenant refuse.":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(exc),
            ) from exc

        if str(exc) == "Google auth non configuree.":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentification Google indisponible.",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requete Google invalide.",
        ) from exc


@router.post(
    "/auth/google/link",
    response_model=GoogleLinkResponse,
)
def link_google_identity(
    request: GoogleLinkRequest,
    http_request: Request,
    current_user: AuthenticatedUser = Depends(get_current_user),
    use_case: LinkGoogleIdentity = Depends(get_link_google_identity_use_case),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    client_ip = get_client_ip(http_request)
    for key in (
        f"google_link:user:{current_user.id}",
        f"google_link:ip:{client_ip}",
    ):
        result = rate_limiter.check_and_record(
            key=key, limit=5, window_seconds=300
        )
        if not result.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Trop de tentatives de liaison Google.",
                headers={"Retry-After": str(result.retry_after)},
            )
    try:
        use_case.execute(
            current_user.id,
            request.id_token,
            request.nonce,
            request.password,
            request.totp_code,
        )
    except ValueError as exc:
        if str(exc) == "Google auth non configuree.":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentification Google indisponible.",
            ) from exc
        if str(exc) in {
            "Identite Google deja liee.",
            "Une identite Google est deja liee.",
        }:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Identite Google deja liee.",
            ) from exc
        if str(exc) == "Reauthentification EduNova refusee.":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Reauthentification EduNova requise.",
            ) from exc
        if str(exc) == "Nonce Google invalide.":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentification Google refusee.",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de lier cette identite Google.",
        ) from exc

    return GoogleLinkResponse(linked=True)


@router.post(
    "/auth/refresh",
    response_model=LoginUserResponse,
)
def refresh_access_token(
    request: RefreshTokenRequest,
    use_case: RefreshAccessToken = Depends(
        get_refresh_access_token_use_case
    ),
):
    try:
        result = use_case.execute(
            refresh_token=request.refresh_token,
        )

        return LoginUserResponse(
            authenticated=True,
            two_factor_required=False,
            two_factor_token=None,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


@router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout_user(
    request: RefreshTokenRequest,
    use_case: LogoutUser = Depends(get_logout_user_use_case),
):
    """Revoke the presented refresh token.

    Compatible with the existing refresh jti blacklist. Access tokens are
    not revoked and expire naturally.
    """
    try:
        use_case.execute(refresh_token=request.refresh_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post(
    "/auth/2fa/setup/{user_id}",
    response_model=EnableTwoFactorResponse,
)
def enable_two_factor(
    user_id: UUID,
    use_case: EnableTwoFactor = Depends(get_enable_two_factor_use_case),
    current_user=Depends(require_role("ADMIN")),
    tenant_context=Depends(get_tenant_context),
):
    try:
        result = use_case.execute(
            user_id=user_id,
            tenant_id=tenant_context.tenant_id,
        )

        return EnableTwoFactorResponse(
            secret=result.secret,
            provisioning_uri=result.provisioning_uri,
        )

    except ValueError as exc:
        if str(exc) == "Utilisateur introuvable.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/auth/2fa/verify/{user_id}",
    response_model=VerifyTwoFactorResponse,
)
def verify_two_factor(
    user_id: UUID,
    request: VerifyTwoFactorRequest,
    use_case: VerifyTwoFactor = Depends(get_verify_two_factor_use_case),
    current_user=Depends(require_role("ADMIN")),
    tenant_context=Depends(get_tenant_context),
):
    try:
        verified = use_case.execute(
            user_id=user_id,
            tenant_id=tenant_context.tenant_id,
            code=request.code,
        )

        return VerifyTwoFactorResponse(
            verified=verified,
        )

    except ValueError as exc:
        if str(exc) == "Utilisateur introuvable.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/auth/2fa/login",
    response_model=VerifyLoginTwoFactorResponse,
)
def verify_login_two_factor(
    request: VerifyLoginTwoFactorRequest,
    http_request: Request,
    use_case: VerifyLoginTwoFactor = Depends(
        get_verify_login_two_factor_use_case
    ),
    rate_limiter: RateLimiter = Depends(get_rate_limiter),
):
    client_ip = get_client_ip(http_request)
    ip_result = rate_limiter.check_and_record(
        key=f"2fa_login:ip:{client_ip}",
        limit=10,
        window_seconds=60,
    )
    if not ip_result.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Trop de tentatives 2FA. Veuillez reessayer plus tard.",
            headers={"Retry-After": str(ip_result.retry_after)},
        )

    try:
        application_request = ApplicationVerifyLoginTwoFactorRequest(
            two_factor_token=request.two_factor_token,
            code=request.code,
        )
        result = use_case.execute(application_request)

        return VerifyLoginTwoFactorResponse(
            authenticated=True,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
        )

    except ValueError as exc:
        if str(exc) == "Nombre maximal de tentatives 2FA depasse.":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Nombre maximal de tentatives 2FA depasse. Veuillez vous reconnecter.",
                headers={"Retry-After": "300"},
            ) from exc

        if str(exc) in {
            "Token 2FA deja consomme.",
            "Le token 2FA est invalide.",
            "Code 2FA invalide.",
            "Code 2FA deja utilise.",
        }:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc

        if str(exc) == "Utilisateur introuvable.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/auth/me",
    response_model=MeResponse,
)
def get_me(
    current_user: AuthenticatedUser = Depends(get_current_user),
    tenant_context: TenantContext = Depends(get_tenant_context),
    membership_repository: MembershipRepository = Depends(get_membership_repository),
):
    membership = membership_repository.find_by_user_and_tenant(
        current_user.id,
        tenant_context.tenant_id,
    )
    if membership is None or not membership.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces tenant refuse.",
        )

    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        role=membership.role,
        is_active=current_user.is_active,
        two_factor_enabled=current_user.two_factor_enabled,
    )
