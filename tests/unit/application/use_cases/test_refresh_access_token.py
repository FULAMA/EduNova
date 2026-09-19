from uuid import uuid4

import pytest

from src.infrastructure.security.jwt_service import JwtService
from src.application.use_cases.refresh_access_token import RefreshAccessToken
from src.domain.entities.user import User
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.in_memory_refresh_token_repository import (
    InMemoryRefreshTokenRepository,
)
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.infrastructure.repositories.sqlite_membership_repository import (
    SQLiteMembershipRepository,
)
from src.infrastructure.repositories.sqlite_tenant_repository import (
    SQLiteTenantRepository,
)
from tests.support.tenant import TEST_TENANT_ID, seed_membership


JWT_SECRET = "edunova-test-secret-key-32-bytes-minimum"


def create_environment():
    database = SQLiteDatabase(":memory:")
    database.initialize()

    user_repository = SQLiteUserRepository(database)
    membership_repository = SQLiteMembershipRepository(database)
    tenant_repository = SQLiteTenantRepository(database)
    refresh_token_repository = InMemoryRefreshTokenRepository()
    jwt_service = JwtService(secret_key=JWT_SECRET)

    use_case = RefreshAccessToken(
        user_repository=user_repository,
        membership_repository=membership_repository,
        tenant_repository=tenant_repository,
        refresh_token_repository=refresh_token_repository,
        jwt_service=jwt_service,
    )

    return (
        user_repository,
        refresh_token_repository,
        jwt_service,
        use_case,
    )


def create_user(user_repository, is_active=True):
    user = User(
        id=uuid4(),
        email=f"{uuid4()}@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        is_active=is_active,
    )

    user_repository.save(user)
    seed_membership(
        type("Container", (), {"_database": user_repository._database})(),
        user.id,
        tenant_id=TEST_TENANT_ID,
        role=user.role,
    )

    return user


def test_refresh_returns_new_tokens():
    user_repository, _, jwt_service, use_case = create_environment()

    user = create_user(user_repository)

    old_refresh_token = jwt_service.create_refresh_token(user.id, tenant_id=TEST_TENANT_ID)

    result = use_case.execute(old_refresh_token)

    assert result.access_token
    assert result.refresh_token
    assert result.access_token != old_refresh_token
    assert result.refresh_token != old_refresh_token


def test_old_refresh_token_is_revoked():
    user_repository, refresh_repository, jwt_service, use_case = (
        create_environment()
    )

    user = create_user(user_repository)

    old_refresh_token = jwt_service.create_refresh_token(user.id, tenant_id=TEST_TENANT_ID)

    use_case.execute(old_refresh_token)

    payload = jwt_service.decode_refresh_token(old_refresh_token)

    assert refresh_repository.is_revoked(payload["jti"]) is True


def test_revoked_refresh_token_is_rejected():
    user_repository, refresh_repository, jwt_service, use_case = (
        create_environment()
    )

    user = create_user(user_repository)

    refresh_token = jwt_service.create_refresh_token(user.id, tenant_id=TEST_TENANT_ID)

    payload = jwt_service.decode_refresh_token(refresh_token)

    refresh_repository.revoke(payload["jti"])

    with pytest.raises(ValueError, match="Token refresh revoque"):
        use_case.execute(refresh_token)


def test_unknown_user_is_rejected():
    _, _, jwt_service, use_case = create_environment()

    fake_user_id = uuid4()
    refresh_token = jwt_service.create_refresh_token(fake_user_id, tenant_id=TEST_TENANT_ID)

    with pytest.raises(ValueError, match="Utilisateur introuvable"):
        use_case.execute(refresh_token)


def test_inactive_user_is_rejected():
    user_repository, _, jwt_service, use_case = create_environment()

    user = create_user(user_repository, is_active=False)

    refresh_token = jwt_service.create_refresh_token(user.id, tenant_id=TEST_TENANT_ID)

    with pytest.raises(ValueError, match="Compte desactive"):
        use_case.execute(refresh_token)


def test_access_token_cannot_be_used_as_refresh_token():
    _, _, jwt_service, use_case = create_environment()

    user_id = uuid4()

    access_token = jwt_service.create_access_token(
        user_id=user_id,
        role="ADMIN",
        tenant_id=TEST_TENANT_ID,
    )

    with pytest.raises(ValueError, match="Token refresh requis"):
        use_case.execute(access_token)


def test_invalid_refresh_token_is_rejected():
    _, _, _, use_case = create_environment()

    with pytest.raises(ValueError):
        use_case.execute("token-invalide")

