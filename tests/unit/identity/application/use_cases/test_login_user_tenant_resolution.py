import time
from uuid import uuid4

import jwt
import pytest

from src.identity.application.dto.login_user_request import LoginUserRequest
from src.identity.application.dto.select_tenant_context_request import (
    SelectTenantContextRequest,
)
from src.identity.application.interfaces.password_hasher import PasswordHasher
from src.identity.application.interfaces.two_factor_service import TwoFactorService
from src.identity.application.use_cases.login_user import (
    LoginUser,
)
from src.identity.application.use_cases.select_tenant_context import (
    SelectTenantContext,
)
from src.identity.domain.entities.user import User
from src.identity.infrastructure.security.in_memory_rate_limiter import (
    InMemoryRateLimiter,
)
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.infrastructure.security.jwt_service import JwtService
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant
from src.tenancy.infrastructure.repositories.sqlite_membership_repository import (
    SQLiteMembershipRepository,
)
from src.tenancy.infrastructure.repositories.sqlite_tenant_repository import (
    SQLiteTenantRepository,
)


class DummyPasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return f"hashed_{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed_{password}"


class DummyTwoFactorService(TwoFactorService):
    def generate_secret(self) -> str:
        return "JBSWY3DPEHPK3PXP"

    def generate_provisioning_uri(self, email: str, secret: str) -> str:
        return f"otpauth://totp/EduNova:{email}?secret={secret}"

    def verify_code(self, secret: str, code: str) -> bool:
        return code == "123456"


def setup_auth_environment(tmp_path):
    db_path = str(tmp_path / "test_auth_resolution.db")
    database = SQLiteDatabase(db_path)
    with database.connect() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                active INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                two_factor_enabled INTEGER NOT NULL,
                two_factor_secret TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memberships (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                role TEXT NOT NULL,
                active INTEGER NOT NULL,
                UNIQUE (user_id, tenant_id),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
            )
            """
        )

    tenant_repo = SQLiteTenantRepository(database)
    user_repo = SQLiteUserRepository(database)
    membership_repo = SQLiteMembershipRepository(database)
    jwt_service = JwtService(
        secret_key="a" * 32,
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )
    hasher = DummyPasswordHasher()
    two_factor = DummyTwoFactorService()
    rate_limiter = InMemoryRateLimiter()

    login_use_case = LoginUser(
        user_repository=user_repo,
        membership_repository=membership_repo,
        tenant_repository=tenant_repo,
        password_hasher=hasher,
        two_factor_service=two_factor,
        jwt_service=jwt_service,
    )

    select_context_use_case = SelectTenantContext(
        user_repository=user_repo,
        membership_repository=membership_repo,
        tenant_repository=tenant_repo,
        jwt_service=jwt_service,
        rate_limiter=rate_limiter,
    )

    return (
        database,
        tenant_repo,
        user_repo,
        membership_repo,
        jwt_service,
        hasher,
        rate_limiter,
        login_use_case,
        select_context_use_case,
    )


# 1. Login mono-tenant sans tenant_id
def test_login_mono_tenant_without_tenant_id(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, _ = (
        setup_auth_environment(tmp_path)
    )

    tenant = Tenant(id=uuid4(), name="École Boboto", slug="boboto", active=True)
    tenant_repo.save(tenant)

    user = User(
        id=uuid4(),
        email="prof@boboto.cd",
        password_hash=hasher.hash("Secret123!"),
        role="PROF",
        is_active=True,
    )
    user_repo.save(user)

    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        tenant_id=tenant.id,
        role="PROF",
        active=True,
    )
    membership_repo.save(membership)

    req = LoginUserRequest(email="prof@boboto.cd", password="Secret123!", tenant_id=None)
    resp = login_uc.execute(req)

    assert resp.authenticated is True
    assert resp.two_factor_required is False
    assert resp.access_token is not None
    assert resp.refresh_token is not None
    assert resp.tenant_selection_required is False


# 2. Login mono-tenant avec tenant_id explicite (rétrocompatibilité)
def test_login_mono_tenant_with_explicit_tenant_id(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, _ = (
        setup_auth_environment(tmp_path)
    )

    tenant = Tenant(id=uuid4(), name="École Boboto", slug="boboto", active=True)
    tenant_repo.save(tenant)

    user = User(
        id=uuid4(),
        email="prof@boboto.cd",
        password_hash=hasher.hash("Secret123!"),
        role="PROF",
        is_active=True,
    )
    user_repo.save(user)

    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        tenant_id=tenant.id,
        role="PROF",
        active=True,
    )
    membership_repo.save(membership)

    req = LoginUserRequest(email="prof@boboto.cd", password="Secret123!", tenant_id=tenant.id)
    resp = login_uc.execute(req)

    assert resp.authenticated is True
    assert resp.access_token is not None


# 3. Login multi-tenant sans tenant_id
def test_login_multi_tenant_without_tenant_id(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, _ = (
        setup_auth_environment(tmp_path)
    )

    t1 = Tenant(id=uuid4(), name="École A", slug="ecole-a", active=True)
    t2 = Tenant(id=uuid4(), name="École B", slug="ecole-b", active=True)
    tenant_repo.save(t1)
    tenant_repo.save(t2)

    user = User(
        id=uuid4(),
        email="expert@edunova.cd",
        password_hash=hasher.hash("Secret123!"),
        role="ADMIN",
        is_active=True,
    )
    user_repo.save(user)

    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=t1.id, role="ADMIN", active=True))
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=t2.id, role="DIRECTION", active=True))

    req = LoginUserRequest(email="expert@edunova.cd", password="Secret123!", tenant_id=None)
    resp = login_uc.execute(req)

    assert resp.authenticated is False
    assert resp.tenant_selection_required is True
    assert resp.tenant_selection_token is not None
    assert resp.access_token is None
    assert resp.refresh_token is None
    assert len(resp.available_tenants) == 2
    slugs = {opt.tenant_slug for opt in resp.available_tenants}
    assert slugs == {"ecole-a", "ecole-b"}


# 4. Sélection d'un tenant autorisé via jeton temporaire
def test_select_tenant_context_authorized(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, select_uc = (
        setup_auth_environment(tmp_path)
    )

    t1 = Tenant(id=uuid4(), name="École A", slug="ecole-a", active=True)
    t2 = Tenant(id=uuid4(), name="École B", slug="ecole-b", active=True)
    tenant_repo.save(t1)
    tenant_repo.save(t2)

    user = User(
        id=uuid4(),
        email="multi@edunova.cd",
        password_hash=hasher.hash("Secret123!"),
        role="ADMIN",
        is_active=True,
    )
    user_repo.save(user)

    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=t1.id, role="ADMIN", active=True))
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=t2.id, role="DIRECTION", active=True))

    login_resp = login_uc.execute(LoginUserRequest(email="multi@edunova.cd", password="Secret123!"))
    token = login_resp.tenant_selection_token
    assert token is not None

    select_req = SelectTenantContextRequest(tenant_selection_token=token, tenant_id=t1.id)
    final_resp = select_uc.execute(select_req)

    assert final_resp.authenticated is True
    assert final_resp.access_token is not None
    assert final_resp.refresh_token is not None


# 5. Sélection d'un tenant non autorisé
def test_select_tenant_context_unauthorized(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, select_uc = (
        setup_auth_environment(tmp_path)
    )

    t1 = Tenant(id=uuid4(), name="École A", slug="ecole-a", active=True)
    t_unauthorized = Tenant(id=uuid4(), name="École C", slug="ecole-c", active=True)
    tenant_repo.save(t1)
    tenant_repo.save(t_unauthorized)

    user = User(
        id=uuid4(),
        email="user@edunova.cd",
        password_hash=hasher.hash("Secret123!"),
        role="PROF",
        is_active=True,
    )
    user_repo.save(user)
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=t1.id, role="PROF", active=True))

    # Create dummy selection token for this user
    _ = login_uc.execute(LoginUserRequest(email="user@edunova.cd", password="Secret123!"))
    # Mono-tenant automatically logs in, but let's test SelectTenantContext with an unauthorized tenant directly
    jwt_svc = JwtService(secret_key="a" * 32)
    fake_token = jwt_svc.create_tenant_selection_token(user.id)

    select_req = SelectTenantContextRequest(
        tenant_selection_token=fake_token,
        tenant_id=t_unauthorized.id,
    )
    with pytest.raises(ValueError, match="Acces tenant refuse."):
        select_uc.execute(select_req)


# 6. Jeton temporaire expiré
def test_select_tenant_context_expired_token(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, _, select_uc = (
        setup_auth_environment(tmp_path)
    )

    tenant = Tenant(id=uuid4(), name="École A", slug="ecole-a", active=True)
    tenant_repo.save(tenant)

    user = User(
        id=uuid4(),
        email="exp@edunova.cd",
        password_hash=hasher.hash("Secret123!"),
        role="PROF",
        is_active=True,
    )
    user_repo.save(user)

    # Manually craft an already expired token
    now = time.time()
    payload = {
        "sub": str(user.id),
        "jti": str(uuid4()),
        "type": "tenant_selection",
        "iat": int(now - 100),
        "exp": int(now - 10),  # expired 10 seconds ago
    }
    expired_token = jwt.encode(payload, "a" * 32, algorithm="HS256")

    select_req = SelectTenantContextRequest(
        tenant_selection_token=expired_token,
        tenant_id=tenant.id,
    )
    with pytest.raises(ValueError, match="Le jeton de selection est invalide ou expire."):
        select_uc.execute(select_req)


# 7. Jeton temporaire réutilisé (anti-replay)
def test_select_tenant_context_anti_replay(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, select_uc = (
        setup_auth_environment(tmp_path)
    )

    t1 = Tenant(id=uuid4(), name="École A", slug="ecole-a", active=True)
    t2 = Tenant(id=uuid4(), name="École B", slug="ecole-b", active=True)
    tenant_repo.save(t1)
    tenant_repo.save(t2)

    user = User(
        id=uuid4(),
        email="replay@edunova.cd",
        password_hash=hasher.hash("Secret123!"),
        role="ADMIN",
        is_active=True,
    )
    user_repo.save(user)
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=t1.id, role="ADMIN", active=True))
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=t2.id, role="ADMIN", active=True))

    login_resp = login_uc.execute(LoginUserRequest(email="replay@edunova.cd", password="Secret123!"))
    token = login_resp.tenant_selection_token
    assert token is not None

    select_req = SelectTenantContextRequest(tenant_selection_token=token, tenant_id=t1.id)

    # First consumption: SUCCESS
    first_resp = select_uc.execute(select_req)
    assert first_resp.authenticated is True

    # Second consumption (Replay): REJECTED
    with pytest.raises(ValueError, match="Jeton de selection deja consomme."):
        select_uc.execute(select_req)


# 8. Membership inactive
def test_login_filters_out_inactive_membership(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, _ = (
        setup_auth_environment(tmp_path)
    )

    t_active = Tenant(id=uuid4(), name="École Active", slug="ecole-active", active=True)
    t_inactive = Tenant(id=uuid4(), name="École Inactive", slug="ecole-inactive", active=True)
    tenant_repo.save(t_active)
    tenant_repo.save(t_inactive)

    user = User(
        id=uuid4(),
        email="user_mix@edunova.cd",
        password_hash=hasher.hash("Secret123!"),
        role="PROF",
        is_active=True,
    )
    user_repo.save(user)

    # One active membership, one INACTIVE membership
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=t_active.id, role="PROF", active=True))
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=t_inactive.id, role="PROF", active=False))

    # The inactive membership is ignored, so user is treated as mono-tenant for the active one!
    resp = login_uc.execute(LoginUserRequest(email="user_mix@edunova.cd", password="Secret123!"))
    assert resp.authenticated is True
    assert resp.tenant_selection_required is False


# 9. Utilisateur sans membership active
def test_login_rejects_user_without_active_memberships(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, _ = (
        setup_auth_environment(tmp_path)
    )

    tenant = Tenant(id=uuid4(), name="École A", slug="ecole-a", active=True)
    tenant_repo.save(tenant)

    user = User(
        id=uuid4(),
        email="orphan@edunova.cd",
        password_hash=hasher.hash("Secret123!"),
        role="PROF",
        is_active=True,
    )
    user_repo.save(user)

    # Inactive membership
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=tenant.id, role="PROF", active=False))

    with pytest.raises(ValueError, match="Aucun etablissement actif associe a ce compte."):
        login_uc.execute(LoginUserRequest(email="orphan@edunova.cd", password="Secret123!"))


# 10. Mot de passe incorrect
def test_login_rejects_wrong_password_uniform_error(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, _ = (
        setup_auth_environment(tmp_path)
    )

    tenant = Tenant(id=uuid4(), name="École A", slug="ecole-a", active=True)
    tenant_repo.save(tenant)

    user = User(
        id=uuid4(),
        email="wrong_pass@edunova.cd",
        password_hash=hasher.hash("CorrectPassword1!"),
        role="PROF",
        is_active=True,
    )
    user_repo.save(user)
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=tenant.id, role="PROF", active=True))

    with pytest.raises(ValueError, match="Identifiants invalides."):
        login_uc.execute(LoginUserRequest(email="wrong_pass@edunova.cd", password="IncorrectPassword!"))


# 11. Compte inexistant (anti-énumération)
def test_login_rejects_nonexistent_account_uniform_error(tmp_path):
    _, _, _, _, _, _, _, login_uc, _ = setup_auth_environment(tmp_path)

    with pytest.raises(ValueError, match="Identifiants invalides."):
        login_uc.execute(LoginUserRequest(email="nonexistent@edunova.cd", password="AnyPassword!"))


# 12. Non-régression 2FA
def test_login_with_2fa_mono_tenant(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, _ = (
        setup_auth_environment(tmp_path)
    )

    tenant = Tenant(id=uuid4(), name="École A", slug="ecole-a", active=True)
    tenant_repo.save(tenant)

    user = User(
        id=uuid4(),
        email="totp_user@edunova.cd",
        password_hash=hasher.hash("Secret123!"),
        role="ADMIN",
        is_active=True,
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )
    user_repo.save(user)
    membership_repo.save(Membership(id=uuid4(), user_id=user.id, tenant_id=tenant.id, role="ADMIN", active=True))

    resp = login_uc.execute(LoginUserRequest(email="totp_user@edunova.cd", password="Secret123!"))
    assert resp.authenticated is False
    assert resp.two_factor_required is True
    assert resp.two_factor_token is not None
    assert resp.access_token is None


# 13. Isolation entre deux tenants
def test_tenant_isolation_prevents_cross_tenant_access(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, hasher, _, login_uc, _ = (
        setup_auth_environment(tmp_path)
    )

    t_school_1 = Tenant(id=uuid4(), name="École 1", slug="ecole-1", active=True)
    t_school_2 = Tenant(id=uuid4(), name="École 2", slug="ecole-2", active=True)
    tenant_repo.save(t_school_1)
    tenant_repo.save(t_school_2)

    user1 = User(
        id=uuid4(),
        email="teacher1@ecole1.cd",
        password_hash=hasher.hash("Secret123!"),
        role="PROF",
        is_active=True,
    )
    user_repo.save(user1)
    membership_repo.save(Membership(id=uuid4(), user_id=user1.id, tenant_id=t_school_1.id, role="PROF", active=True))

    # User 1 attempts to log in targeting School 2
    with pytest.raises(ValueError, match="Acces tenant refuse."):
        login_uc.execute(
            LoginUserRequest(
                email="teacher1@ecole1.cd",
                password="Secret123!",
                tenant_id=t_school_2.id,
            )
        )
