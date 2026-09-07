from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services.jwt_service import JwtService
from src.domain.entities.user import User
from src.presentation.api.container import ApplicationContainer


bearer_scheme = HTTPBearer()

optional_bearer_scheme = HTTPBearer(auto_error=False)


def get_application_container() -> ApplicationContainer:
    return ApplicationContainer()


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _authenticate(
    token: str,
    jwt_service: JwtService,
    container: ApplicationContainer,
) -> User:

    try:
        payload = jwt_service.decode_token(token)
    except ValueError as exc:
        raise _unauthorized("Token invalide.") from exc

    if payload.get("type") != "access":
        raise _unauthorized("Token d acces requis.")

    user_id = payload.get("sub")

    if not user_id:
        raise _unauthorized("Token invalide.")

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError) as exc:
        raise _unauthorized("Identifiant utilisateur invalide.") from exc

    user = container.user_repository().find_by_id(user_uuid)

    if user is None:
        raise _unauthorized("Utilisateur introuvable.")

    if not user.is_active:
        raise _unauthorized("Compte desactive.")

    # Un token emis avant un changement de role ne doit pas conserver
    # les privileges de l ancien role.
    if payload.get("role") != user.role:
        raise _unauthorized("Token invalide.")

    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    container: ApplicationContainer = Depends(get_application_container),
) -> User:

    return _authenticate(
        credentials.credentials,
        container.jwt_service(),
        container,
    )


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        optional_bearer_scheme
    ),
    container: ApplicationContainer = Depends(get_application_container),
) -> User | None:

    if credentials is None:
        return None

    return _authenticate(
        credentials.credentials,
        container.jwt_service(),
        container,
    )


def require_role(*allowed_roles: str):
    if not allowed_roles:
        raise ValueError("Au moins un role est requis.")

    def role_dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acces interdit.",
            )

        return current_user

    return role_dependency


def enforce_auth_rate_limit(
    request: Request,
    container: ApplicationContainer = Depends(get_application_container),
) -> None:
    """Protege les routes d authentification contre le bruteforce."""

    limiter = container.auth_rate_limiter()

    client_host = request.client.host if request.client else "unknown"

    key = f"{request.url.path}:{client_host}"

    if limiter.is_allowed(key):
        return

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Trop de tentatives. Reessayez plus tard.",
        headers={
            "Retry-After": str(limiter.retry_after_seconds(key)),
        },
    )
