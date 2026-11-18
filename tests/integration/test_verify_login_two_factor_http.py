import pyotp
from uuid import uuid4

from fastapi.testclient import TestClient

from src.infrastructure.security.jwt_service import JwtService
from src.identity.infrastructure.security.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from src.identity.domain.entities.user import User
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership




def create_test_environment():
    container = ApplicationContainer(
        database_path=":memory:"
    )

    repository = SQLiteUserRepository(
        container._database
    )

    password_hasher = Argon2PasswordHasher()

    secret = pyotp.random_base32()

    user = User(
        id=uuid4(),
        email="admin@edunova.com",
        password_hash=password_hasher.hash(
            "EduNova@2026"
        ),
        role="ADMIN",
        is_active=True,
        two_factor_enabled=True,
        two_factor_secret=secret,
    )

    repository.save(user)

    seed_membership(
        container,
        user.id,
        tenant_id=TEST_TENANT_ID,
        role=user.role,
    )

    app = create_app(container)

    client = TestClient(app)

    return client, user, secret


def test_verify_login_two_factor_http_success():
    client, user, secret = create_test_environment()

    jwt_service = JwtService(
        secret_key=TEST_JWT_SECRET
    )

    pending_token = jwt_service.create_two_factor_token(
        user_id=user.id,
        tenant_id=TEST_TENANT_ID,
    )

    code = pyotp.TOTP(secret).now()

    response = client.post(
        "/auth/2fa/login",
        json={
            "two_factor_token": pending_token,
            "code": code,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["authenticated"] is True
    assert data["access_token"]
    assert data["refresh_token"]


def test_verify_login_two_factor_http_rejects_invalid_code():
    client, user, _ = create_test_environment()

    jwt_service = JwtService(
        secret_key=TEST_JWT_SECRET
    )

    pending_token = jwt_service.create_two_factor_token(
        user_id=user.id,
        tenant_id=TEST_TENANT_ID,
    )

    response = client.post(
        "/auth/2fa/login",
        json={
            "two_factor_token": pending_token,
            "code": "000000",
        },
    )

    assert response.status_code == 401  # Code invalide = erreur auth


def test_verify_login_two_factor_http_rejects_non_pending_token():
    client, user, _ = create_test_environment()

    jwt_service = JwtService(
        secret_key=TEST_JWT_SECRET
    )

    access_token = jwt_service.create_access_token(
        user_id=user.id,
        role=user.role,
        tenant_id=TEST_TENANT_ID,
    )

    response = client.post(
        "/auth/2fa/login",
        json={
            "two_factor_token": access_token,
            "code": "123456",
        },
    )

    assert response.status_code == 401  # Token non-pending = erreur auth


def test_verify_login_two_factor_http_rejects_unknown_user():
    client, _, _ = create_test_environment()

    jwt_service = JwtService(
        secret_key=TEST_JWT_SECRET
    )

    pending_token = jwt_service.create_two_factor_token(
        user_id=uuid4(),
        tenant_id=TEST_TENANT_ID,
    )

    code = pyotp.random_base32()

    response = client.post(
        "/auth/2fa/login",
        json={
            "two_factor_token": pending_token,
            "code": pyotp.TOTP(code).now(),
        },
    )

    assert response.status_code == 404





def test_verify_login_two_factor_http_rejects_replayed_code_across_sessions():
    client, user, secret = create_test_environment()
    jwt_service = JwtService(secret_key=TEST_JWT_SECRET)

    token1 = jwt_service.create_two_factor_token(user_id=user.id, tenant_id=TEST_TENANT_ID)
    code = pyotp.TOTP(secret).now()

    # Session 1 succeeds
    resp1 = client.post("/auth/2fa/login", json={"two_factor_token": token1, "code": code})
    assert resp1.status_code == 200

    # Session 2 attempts to use same code
    token2 = jwt_service.create_two_factor_token(user_id=user.id, tenant_id=TEST_TENANT_ID)
    resp2 = client.post("/auth/2fa/login", json={"two_factor_token": token2, "code": code})
    assert resp2.status_code == 401
    assert "Code 2FA deja utilise" in resp2.json()["detail"]


def test_verify_login_two_factor_http_persists_across_restart():
    import gc
    import tempfile
    from pathlib import Path
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    db_path = temp_file.name

    try:
        # First process instance
        container1 = ApplicationContainer(database_path=db_path)
        hasher = Argon2PasswordHasher()
        secret = pyotp.random_base32()
        user = User(
            id=uuid4(),
            email="restart-2fa@edunova.com",
            password_hash=hasher.hash("EduNova@2026"),
            role="ADMIN",
            is_active=True,
            two_factor_enabled=True,
            two_factor_secret=secret,
        )
        container1._user_repository().save(user)
        seed_membership(container1, user.id, tenant_id=TEST_TENANT_ID, role="ADMIN")
        client1 = TestClient(create_app(container1))

        jwt_service = container1._jwt_service()
        token1 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
        code = pyotp.TOTP(secret).now()

        # Session 1 on instance 1 succeeds
        resp1 = client1.post("/auth/2fa/login", json={"two_factor_token": token1, "code": code})
        assert resp1.status_code == 200

        # Simulate restart
        del client1
        del container1
        gc.collect()

        # Second process instance on same db
        container2 = ApplicationContainer(database_path=db_path)
        client2 = TestClient(create_app(container2))
        token2 = container2._jwt_service().create_two_factor_token(user.id, TEST_TENANT_ID)

        # Replay attempt on instance 2 is rejected
        resp2 = client2.post("/auth/2fa/login", json={"two_factor_token": token2, "code": code})
        assert resp2.status_code == 401
        assert "Code 2FA deja utilise" in resp2.json()["detail"]

        del client2
        del container2
    finally:
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


def test_verify_login_two_factor_http_concurrent_requests():
    import gc
    import tempfile
    from pathlib import Path
    from concurrent.futures import ThreadPoolExecutor

    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    db_path = temp_file.name

    try:
        container = ApplicationContainer(database_path=db_path)
        hasher = Argon2PasswordHasher()
        secret = pyotp.random_base32()
        user = User(
            id=uuid4(),
            email="concurrent-2fa@edunova.com",
            password_hash=hasher.hash("EduNova@2026"),
            role="ADMIN",
            is_active=True,
            two_factor_enabled=True,
            two_factor_secret=secret,
        )
        container._user_repository().save(user)
        seed_membership(container, user.id, tenant_id=TEST_TENANT_ID, role="ADMIN")
        client = TestClient(create_app(container))

        jwt_service = container._jwt_service()
        token1 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
        token2 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
        code = pyotp.TOTP(secret).now()

        def submit(token):
            return client.post("/auth/2fa/login", json={"two_factor_token": token, "code": code})

        with ThreadPoolExecutor(max_workers=2) as executor:
            fut1 = executor.submit(submit, token1)
            fut2 = executor.submit(submit, token2)
            res1 = fut1.result()
            res2 = fut2.result()

        statuses = sorted([res1.status_code, res2.status_code])
        # Exactly one 200 OK and one 401 Unauthorized
        assert statuses == [200, 401]
    finally:
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass
