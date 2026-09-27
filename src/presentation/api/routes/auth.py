from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.identity.application.use_cases.enable_two_factor import EnableTwoFactor
from src.identity.application.use_cases.login_user import LoginUser
from src.identity.application.use_cases.refresh_access_token import RefreshAccessToken
from src.identity.application.dto.register_user_request import RegisterUserRequest as ApplicationRegisterUserRequest
from src.identity.application.dto.login_user_request import LoginUserRequest as ApplicationLoginUserRequest
from src.identity.application.dto.verify_login_two_factor_request import VerifyLoginTwoFactorRequest as ApplicationVerifyLoginTwoFactorRequest
from src.identity.application.use_cases.register_user import RegisterUser
from src.identity.application.use_cases.verify_login_two_factor import VerifyLoginTwoFactor
from src.identity.application.use_cases.verify_two_factor import VerifyTwoFactor

from src.identity.application.dto.authenticated_user import AuthenticatedUser

from src.presentation.api.dependencies.auth import (
    get_current_user,
    get_tenant_context,
    require_role,
)

from src.presentation.api.dependencies import (
    get_enable_two_factor_use_case,
    get_login_user_use_case,
    get_refresh_access_token_use_case,
    get_register_user_use_case,
    get_verify_login_two_factor_use_case,
    get_verify_two_factor_use_case,
)

from src.presentation.api.schemas.enable_two_factor_response import (
    EnableTwoFactorResponse,
)
from src.presentation.api.schemas.me_response import MeResponse
from src.presentation.api.schemas.login_user_request import LoginUserRequest
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

router = APIRouter()


@router.post(
    "/auth/register",
    response_model=RegisterUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: RegisterUserRequest,
    use_case: RegisterUser = Depends(get_register_user_use_case),
):
    try:
        application_request = ApplicationRegisterUserRequest(
            email=request.email,
            password=request.password,
            role=request.role,
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
    use_case: LoginUser = Depends(get_login_user_use_case),
):
    try:
        application_request = ApplicationLoginUserRequest(
            email=request.email,
            password=request.password,
            tenant_id=request.tenant_id,
        )
        result = use_case.execute(application_request)

        return LoginUserResponse(
            authenticated=result.authenticated,
            two_factor_required=result.two_factor_required,
            two_factor_token=result.two_factor_token,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
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

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


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
    use_case: VerifyLoginTwoFactor = Depends(
        get_verify_login_two_factor_use_case
    ),
):
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
):
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        two_factor_enabled=current_user.two_factor_enabled,
    )
