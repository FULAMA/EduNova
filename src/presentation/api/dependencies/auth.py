from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.interfaces.jwt_service import JwtService
from src.application.interfaces.user_repository import UserRepository
from src.application.interfaces.membership_repository import MembershipRepository
from src.application.interfaces.tenant_repository import TenantRepository
from src.presentation.api.dependencies import (
    get_jwt_service,
    get_membership_repository,
    get_tenant_repository,
    get_user_repository,
)
from src.application.context.tenant_context import TenantContext
from src.domain.entities.user import User


bearer_scheme = HTTPBearer()



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> User:

    token = credentials.credentials


    try:
        payload = jwt_service.decode_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d acces requis.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant utilisateur invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = user_repository.find_by_id(user_uuid)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte desactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_tenant_context(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    jwt_service: JwtService = Depends(get_jwt_service),
    tenant_repository: TenantRepository = Depends(get_tenant_repository),
    membership_repository: MembershipRepository = Depends(get_membership_repository),
) -> TenantContext:
    try:
        payload = jwt_service.decode_token(credentials.credentials)

        if payload.get("type") != "access":
            raise ValueError("Access token requis.")

        user_id = UUID(payload["sub"])
        tenant_id = UUID(payload["tenant_id"])

    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant JWT invalide.",
        ) from exc

    tenant = tenant_repository.find_by_id(tenant_id)

    membership = (
        membership_repository.find_by_user_and_tenant(user_id, tenant_id)
    )

    if (
        tenant is None
        or not tenant.active
        or membership is None
        or not membership.active
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces tenant refuse.",
        )

    return TenantContext(tenant_id)


def require_role(*allowed_roles: str):
    if not allowed_roles:
        raise ValueError("Au moins un role est requis.")

    def role_dependency(
        current_user: User = Depends(get_current_user),
        tenant_context: TenantContext = Depends(get_tenant_context),
        membership_repository: MembershipRepository = Depends(get_membership_repository),
    ) -> User:
        membership = (
            membership_repository.find_by_user_and_tenant(
                current_user.id,
                tenant_context.tenant_id,
            )
        )

        if membership is None or not membership.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acces tenant refuse.",
            )

        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acces interdit.",
            )

        return current_user

    return role_dependency











