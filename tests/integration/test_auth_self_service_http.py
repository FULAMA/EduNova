from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import gc
from pathlib import Path
import tempfile
from uuid import UUID, uuid4

import jwt as pyjwt
from fastapi.testclient import TestClient

from src.identity.domain.entities.user import User
from src.identity.infrastructure.security.argon2_password_hasher import Argon2PasswordHasher
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import seed_membership, seed_tenant


def create_test_setup(database_path=":memory:"):
    container = ApplicationContainer(database_path=database_path)
    app = create_app(container)
    client = TestClient(app)
    return client, container


# ---------------------------------------------------------------------------
# 1. Valid registration (POST /auth/register-establishment -> HTTP 201)
# ---------------------------------------------------------------------------
def test_register_establishment_success():
    client, _ = create_test_setup()
    payload = {
        "school_name": "Lycée d'Excellence Cheikh Hamidou Kane",
        "admin_name": "Amadou Kane",
        "email": "amadou.kane@excellence.sn",
        "password": "Password123!",
    }
    response = client.post("/auth/register-establishment", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert UUID(data["tenant_id"])
    assert data["tenant_name"] == "Lycée d'Excellence Cheikh Hamidou Kane"
    assert data["tenant_slug"] == "lycee-d-excellence-cheikh-hamidou-kane"
    assert UUID(data["user_id"])
    assert data["email"] == "amadou.kane@excellence.sn"
    assert data["role"] == "ADMIN"
    assert "password" not in data
    assert "password_hash" not in data


# ---------------------------------------------------------------------------
# 2. Duplicate email registration -> HTTP 409 Conflict
# ---------------------------------------------------------------------------
def test_register_establishment_duplicate_email_conflict():
    client, _ = create_test_setup()
    payload = {
        "school_name": "Lycée Valdiodio Ndiaye",
        "admin_name": "Fatou Ndiaye",
        "email": "fatou.ndiaye@valdiodio.sn",
        "password": "Password123!",
    }
    resp1 = client.post("/auth/register-establishment", json=payload)
    assert resp1.status_code == 201

    payload_duplicate = {
        "school_name": "Autre Établissement",
        "admin_name": "Autre Admin",
        "email": "fatou.ndiaye@valdiodio.sn",
        "password": "Password123!",
    }
    resp2 = client.post("/auth/register-establishment", json=payload_duplicate)
    assert resp2.status_code == 409
    assert "utilisee" in resp2.json()["detail"]


# ---------------------------------------------------------------------------
# 3. Invalid registration data -> HTTP 400 or 422
# ---------------------------------------------------------------------------
def test_register_establishment_invalid_data_and_forbidden_fields():
    client, _ = create_test_setup()

    # Invalid email
    resp_invalid_email = client.post(
        "/auth/register-establishment",
        json={
            "school_name": "École B",
            "admin_name": "Jean Dupont",
            "email": "not-an-email",
            "password": "Password123!",
        },
    )
    assert resp_invalid_email.status_code in {400, 422}

    # Password too short (< 8 chars)
    resp_short_pwd = client.post(
        "/auth/register-establishment",
        json={
            "school_name": "École B",
            "admin_name": "Jean Dupont",
            "email": "jean@ecoleb.sn",
            "password": "short",
        },
    )
    assert resp_short_pwd.status_code == 422

    # Injected forbidden field (extra="forbid")
    resp_injected_role = client.post(
        "/auth/register-establishment",
        json={
            "school_name": "École C",
            "admin_name": "Jean Dupont",
            "email": "jean@ecolec.sn",
            "password": "Password123!",
            "role": "SUPERADMIN",
        },
    )
    assert resp_injected_role.status_code == 422


# ---------------------------------------------------------------------------
# 4. Rate limiting on registration -> HTTP 429 with Retry-After
# ---------------------------------------------------------------------------
def test_register_establishment_rate_limiting():
    client, _ = create_test_setup()

    for i in range(5):
        resp = client.post(
            "/auth/register-establishment",
            json={
                "school_name": f"Établissement {i}",
                "admin_name": f"Admin {i}",
                "email": f"admin{i}@rate.sn",
                "password": "Password123!",
            },
        )
        assert resp.status_code == 201

    # 6th attempt should be blocked by rate limiter (limit is 5 / 15min)
    resp_blocked = client.post(
        "/auth/register-establishment",
        json={
            "school_name": "Établissement 6",
            "admin_name": "Admin 6",
            "email": "admin6@rate.sn",
            "password": "Password123!",
        },
    )
    assert resp_blocked.status_code == 429
    assert "Retry-After" in resp_blocked.headers
    assert int(resp_blocked.headers["Retry-After"]) > 0


# ---------------------------------------------------------------------------
# 5. Mono-tenant login without tenant_id -> HTTP 200 with tokens
# ---------------------------------------------------------------------------
def test_login_mono_tenant_without_tenant_id():
    client, _ = create_test_setup()

    # Register establishment
    reg_resp = client.post(
        "/auth/register-establishment",
        json={
            "school_name": "Collège Moderne",
            "admin_name": "Moussa Diop",
            "email": "moussa.diop@moderne.sn",
            "password": "Password123!",
        },
    )
    assert reg_resp.status_code == 201

    # Login without tenant_id
    login_resp = client.post(
        "/auth/login",
        json={
            "email": "moussa.diop@moderne.sn",
            "password": "Password123!",
        },
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["authenticated"] is True
    assert data["tenant_selection_required"] is False
    assert data["access_token"] is not None
    assert data["refresh_token"] is not None


# ---------------------------------------------------------------------------
# 6. Multi-tenant login without tenant_id -> tenant_selection_required
# ---------------------------------------------------------------------------
def test_login_multi_tenant_without_tenant_id():
    client, container = create_test_setup()
    hasher = Argon2PasswordHasher()

    # Create user with 2 active memberships
    user = User(
        id=uuid4(),
        email="multi@edunova.com",
        password_hash=hasher.hash("Password123!"),
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user)

    tenant1 = uuid4()
    tenant2 = uuid4()
    seed_membership(container, user.id, tenant_id=tenant1, role="ADMIN")
    seed_membership(container, user.id, tenant_id=tenant2, role="TEACHER")

    login_resp = client.post(
        "/auth/login",
        json={
            "email": "multi@edunova.com",
            "password": "Password123!",
        },
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["authenticated"] is False
    assert data["tenant_selection_required"] is True
    assert data["tenant_selection_token"] is not None
    assert len(data["available_tenants"]) == 2


# ---------------------------------------------------------------------------
# 7. Authorized tenant selection -> HTTP 200 with tokens
# ---------------------------------------------------------------------------
def test_select_tenant_success():
    client, container = create_test_setup()
    hasher = Argon2PasswordHasher()

    user = User(
        id=uuid4(),
        email="multi@edunova.com",
        password_hash=hasher.hash("Password123!"),
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user)

    tenant1 = uuid4()
    tenant2 = uuid4()
    seed_membership(container, user.id, tenant_id=tenant1, role="ADMIN")
    seed_membership(container, user.id, tenant_id=tenant2, role="TEACHER")

    login_resp = client.post(
        "/auth/login",
        json={"email": "multi@edunova.com", "password": "Password123!"},
    )
    data = login_resp.json()
    token = data["tenant_selection_token"]

    select_resp = client.post(
        "/auth/select-tenant",
        json={
            "tenant_selection_token": token,
            "tenant_id": str(tenant2),
        },
    )
    assert select_resp.status_code == 200
    select_data = select_resp.json()
    assert select_data["authenticated"] is True
    assert select_data["access_token"] is not None
    assert select_data["refresh_token"] is not None


# ---------------------------------------------------------------------------
# 8. Unauthorized tenant selection -> HTTP 403 Forbidden
# ---------------------------------------------------------------------------
def test_select_tenant_unauthorized_membership():
    client, container = create_test_setup()
    hasher = Argon2PasswordHasher()

    user = User(
        id=uuid4(),
        email="multi@edunova.com",
        password_hash=hasher.hash("Password123!"),
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user)

    tenant1 = uuid4()
    tenant_unrelated = uuid4()
    seed_membership(container, user.id, tenant_id=tenant1, role="ADMIN")
    seed_tenant(container, tenant_unrelated)

    jwt_service = container._jwt_service()
    selection_token = jwt_service.create_tenant_selection_token(user_id=user.id)

    select_resp = client.post(
        "/auth/select-tenant",
        json={
            "tenant_selection_token": selection_token,
            "tenant_id": str(tenant_unrelated),
        },
    )
    assert select_resp.status_code == 403
    assert "refuse" in select_resp.json()["detail"]


# ---------------------------------------------------------------------------
# 9. Expired tenant selection token -> HTTP 400 Bad Request
# ---------------------------------------------------------------------------
def test_select_tenant_expired_token():
    client, container = create_test_setup()
    hasher = Argon2PasswordHasher()

    user = User(
        id=uuid4(),
        email="multi@edunova.com",
        password_hash=hasher.hash("Password123!"),
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user)
    tenant1 = uuid4()
    seed_membership(container, user.id, tenant_id=tenant1, role="ADMIN")

    # Manually issue expired token
    now = datetime.now(timezone.utc) - timedelta(minutes=10)
    payload = {
        "sub": str(user.id),
        "type": "tenant_selection",
        "jti": str(uuid4()),
        "exp": int(now.timestamp()),
        "iat": int((now - timedelta(minutes=5)).timestamp()),
    }
    expired_token = pyjwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")

    select_resp = client.post(
        "/auth/select-tenant",
        json={
            "tenant_selection_token": expired_token,
            "tenant_id": str(tenant1),
        },
    )
    assert select_resp.status_code == 400
    assert "expire" in select_resp.json()["detail"]


# ---------------------------------------------------------------------------
# 10. Consumed selection token replay -> HTTP 409 Conflict
# ---------------------------------------------------------------------------
def test_select_tenant_replay_prevented():
    client, container = create_test_setup()
    hasher = Argon2PasswordHasher()

    user = User(
        id=uuid4(),
        email="multi@edunova.com",
        password_hash=hasher.hash("Password123!"),
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user)

    tenant1 = uuid4()
    tenant2 = uuid4()
    seed_membership(container, user.id, tenant_id=tenant1, role="ADMIN")
    seed_membership(container, user.id, tenant_id=tenant2, role="TEACHER")

    login_resp = client.post(
        "/auth/login",
        json={"email": "multi@edunova.com", "password": "Password123!"},
    )
    token = login_resp.json()["tenant_selection_token"]

    # First consumption succeeds
    first_resp = client.post(
        "/auth/select-tenant",
        json={"tenant_selection_token": token, "tenant_id": str(tenant1)},
    )
    assert first_resp.status_code == 200

    # Second consumption attempt with the same token must fail with 409 Conflict
    replay_resp = client.post(
        "/auth/select-tenant",
        json={"tenant_selection_token": token, "tenant_id": str(tenant1)},
    )
    assert replay_resp.status_code == 409
    assert "consomme" in replay_resp.json()["detail"]


# ---------------------------------------------------------------------------
# 11. Concurrent requests with same token -> one succeeds, the other gets HTTP 409
# ---------------------------------------------------------------------------
def test_select_tenant_concurrent_consumption():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        container = ApplicationContainer(database_path=db_path)
        app = create_app(container)
        client = TestClient(app)
        hasher = Argon2PasswordHasher()

        user = User(
            id=uuid4(),
            email="concurrent@edunova.com",
            password_hash=hasher.hash("Password123!"),
            role="ADMIN",
            is_active=True,
        )
        container._user_repository().save(user)

        tenant1 = uuid4()
        tenant2 = uuid4()
        seed_membership(container, user.id, tenant_id=tenant1, role="ADMIN")
        seed_membership(container, user.id, tenant_id=tenant2, role="TEACHER")

        token = container._jwt_service().create_tenant_selection_token(user_id=user.id)

        def submit():
            return client.post(
                "/auth/select-tenant",
                json={"tenant_selection_token": token, "tenant_id": str(tenant1)},
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            fut1 = executor.submit(submit)
            fut2 = executor.submit(submit)
            res1 = fut1.result()
            res2 = fut2.result()

        statuses = sorted([res1.status_code, res2.status_code])
        # Exactly one must succeed (200) and one must be rejected (409)
        assert statuses == [200, 409]
    finally:
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 12. Process restart / DB reload then replay attempt -> rejected (persisted in SQLite)
# ---------------------------------------------------------------------------
def test_select_tenant_persists_across_restart():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        # First process instance
        container1 = ApplicationContainer(database_path=db_path)
        app1 = create_app(container1)
        client1 = TestClient(app1)
        hasher = Argon2PasswordHasher()

        user = User(
            id=uuid4(),
            email="restart@edunova.com",
            password_hash=hasher.hash("Password123!"),
            role="ADMIN",
            is_active=True,
        )
        container1._user_repository().save(user)
        tenant1 = uuid4()
        seed_membership(container1, user.id, tenant_id=tenant1, role="ADMIN")

        token = container1._jwt_service().create_tenant_selection_token(user_id=user.id)

        # Consume token in first process instance
        resp1 = client1.post(
            "/auth/select-tenant",
            json={"tenant_selection_token": token, "tenant_id": str(tenant1)},
        )
        assert resp1.status_code == 200

        del client1
        del app1
        del container1
        gc.collect()

        # Simulate process restart by instantiating a completely new container / app on same SQLite db
        container2 = ApplicationContainer(database_path=db_path)
        app2 = create_app(container2)
        client2 = TestClient(app2)

        # Attempt to replay token in new instance
        resp2 = client2.post(
            "/auth/select-tenant",
            json={"tenant_selection_token": token, "tenant_id": str(tenant1)},
        )
        assert resp2.status_code == 409
        assert "consomme" in resp2.json()["detail"]

        del client2
        del app2
        del container2
        gc.collect()
    finally:
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 13. User with 2FA enabled -> two_factor_required=True preserved
# ---------------------------------------------------------------------------
def test_mono_tenant_and_select_tenant_preserves_2fa():
    client, container = create_test_setup()
    hasher = Argon2PasswordHasher()

    user = User(
        id=uuid4(),
        email="2fa_user@edunova.com",
        password_hash=hasher.hash("Password123!"),
        role="ADMIN",
        is_active=True,
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )
    container._user_repository().save(user)

    tenant1 = uuid4()
    seed_membership(container, user.id, tenant_id=tenant1, role="ADMIN")

    # Mono-tenant login with 2FA enabled
    resp = client.post(
        "/auth/login",
        json={"email": "2fa_user@edunova.com", "password": "Password123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["authenticated"] is False
    assert data["two_factor_required"] is True
    assert data["two_factor_token"] is not None
    assert data["access_token"] is None

    # Multi-tenant select-tenant with 2FA enabled
    tenant2 = uuid4()
    seed_membership(container, user.id, tenant_id=tenant2, role="TEACHER")

    selection_token = container._jwt_service().create_tenant_selection_token(user_id=user.id)
    select_resp = client.post(
        "/auth/select-tenant",
        json={"tenant_selection_token": selection_token, "tenant_id": str(tenant1)},
    )
    assert select_resp.status_code == 200
    s_data = select_resp.json()
    assert s_data["authenticated"] is False
    assert s_data["two_factor_required"] is True
    assert s_data["two_factor_token"] is not None
    assert s_data["access_token"] is None


# ---------------------------------------------------------------------------
# 14. Non-regression of /auth/login, /auth/refresh, /auth/logout
# ---------------------------------------------------------------------------
def test_non_regression_login_refresh_logout():
    client, container = create_test_setup()
    hasher = Argon2PasswordHasher()

    user = User(
        id=uuid4(),
        email="classic@edunova.com",
        password_hash=hasher.hash("Password123!"),
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user)
    tenant1 = uuid4()
    seed_membership(container, user.id, tenant_id=tenant1, role="ADMIN")

    # Explicit tenant_id login still works exactly as before
    login_resp = client.post(
        "/auth/login",
        json={
            "email": "classic@edunova.com",
            "password": "Password123!",
            "tenant_id": str(tenant1),
        },
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["authenticated"] is True
    assert login_data["access_token"] is not None
    refresh_token = login_data["refresh_token"]

    # Refresh token works
    refresh_resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    new_access = refresh_resp.json()["access_token"]
    assert new_access is not None

    # Logout works and revokes refresh token
    logout_resp = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout_resp.status_code == 204

    # Subsequent refresh is rejected
    stale_refresh = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert stale_refresh.status_code == 401


# ---------------------------------------------------------------------------
# 15. Cross-tenant isolation verification
# ---------------------------------------------------------------------------
def test_cross_tenant_isolation():
    client, container = create_test_setup()
    hasher = Argon2PasswordHasher()

    # User A belongs strictly to Tenant A
    user_a = User(
        id=uuid4(),
        email="user_a@edunova.com",
        password_hash=hasher.hash("Password123!"),
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user_a)
    tenant_a = uuid4()
    seed_membership(container, user_a.id, tenant_id=tenant_a, role="ADMIN")

    # User B belongs strictly to Tenant B
    user_b = User(
        id=uuid4(),
        email="user_b@edunova.com",
        password_hash=hasher.hash("Password123!"),
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user_b)
    tenant_b = uuid4()
    seed_membership(container, user_b.id, tenant_id=tenant_b, role="ADMIN")

    # User A tries to log in specifying tenant B -> must fail with 403 Forbidden
    cross_login = client.post(
        "/auth/login",
        json={
            "email": "user_a@edunova.com",
            "password": "Password123!",
            "tenant_id": str(tenant_b),
        },
    )
    assert cross_login.status_code == 403
    assert "refuse" in cross_login.json()["detail"]
