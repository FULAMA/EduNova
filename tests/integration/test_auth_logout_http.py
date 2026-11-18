from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt as pyjwt
from fastapi.testclient import TestClient

from src.identity.domain.entities.user import User
from src.infrastructure.security.jwt_service import JwtService
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID, seed_membership


def create_environment():
    container = ApplicationContainer(database_path=":memory:")
    user = User(
        id=uuid4(),
        email="logout@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user)
    seed_membership(container, user.id)
    client = TestClient(create_app(container))
    return client, container, user


def create_refresh_token(user):
    return JwtService(secret_key=TEST_JWT_SECRET).create_refresh_token(
        user_id=user.id,
        tenant_id=TEST_TENANT_ID,
    )


def test_logout_revokes_refresh_token():
    client, _, user = create_environment()
    refresh_token = create_refresh_token(user)

    logout = client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout.status_code == 204

    refresh = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh.status_code == 401


def test_logout_is_idempotent_for_already_revoked_token():
    client, _, user = create_environment()
    refresh_token = create_refresh_token(user)

    first = client.post("/auth/logout", json={"refresh_token": refresh_token})
    second = client.post("/auth/logout", json={"refresh_token": refresh_token})

    assert first.status_code == 204
    assert second.status_code == 204


def test_logout_rejects_invalid_token():
    client, _, _ = create_environment()

    response = client.post(
        "/auth/logout",
        json={"refresh_token": "token-invalide"},
    )

    assert response.status_code == 401  # Token invalide -> ValueError -> 401


def test_logout_rejects_access_token():
    client, _, user = create_environment()
    access_token = JwtService(secret_key=TEST_JWT_SECRET).create_access_token(
        user_id=user.id,
        role=user.role,
        tenant_id=TEST_TENANT_ID,
    )

    response = client.post(
        "/auth/logout",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401  # Token invalide -> ValueError -> 401


# ── LOT B — Tests supplémentaires ────────────────────────────────────────────


def _make_expired_refresh_token(user_id, tenant_id=TEST_TENANT_ID):
    """Crée manuellement un refresh token déjà expiré."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "jti": str(uuid4()),
        "tenant_id": str(tenant_id),
        "type": "refresh",
        "iat": now - timedelta(days=8),
        "exp": now - timedelta(days=1),  # expiré hier
    }
    return pyjwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")


def test_logout_with_expired_token_returns_401():
    """Un token refresh expiré est rejeté avec 401 (Décision 27 — auth proportionnée)."""
    client, _, user = create_environment()
    expired_token = _make_expired_refresh_token(user.id)

    response = client.post(
        "/auth/logout",
        json={"refresh_token": expired_token},
    )

    assert response.status_code == 401  # Token invalide -> ValueError -> 401


def test_logout_cross_user_token_does_not_leak_session():
    """Le token de l'utilisateur B, présenté lors du logout, révoque son jti.
    Il ne doit PAS invalider la session propre à A ni lever d'erreur inattendue.
    (Décision 32 — isolation multi-tenant, Décision 27 — sécurité)
    """
    # Utilisateur A
    client_a, container, user_a = create_environment()
    refresh_a = create_refresh_token(user_a)

    # Utilisateur B dans le même container/tenant (simulation)
    user_b = User(
        id=uuid4(),
        email="user-b@edunova.com",
        password_hash="hashed-password",
        role="ADMIN",
        is_active=True,
    )
    container._user_repository().save(user_b)
    seed_membership(container, user_b.id)
    refresh_b = create_refresh_token(user_b)

    # A essaie de révoquer le token de B — le jti de B est révoqué côté serveur
    # mais ça ne touche PAS le jti de A.
    logout_b = client_a.post("/auth/logout", json={"refresh_token": refresh_b})
    assert logout_b.status_code == 204

    # La session de A doit encore être valide
    refresh_a_response = client_a.post("/auth/refresh", json={"refresh_token": refresh_a})
    assert refresh_a_response.status_code == 200, (
        "La révocation du token de B ne doit pas affecter la session de A"
    )

    # Le token de B est bien révoqué
    refresh_b_response = client_a.post("/auth/refresh", json={"refresh_token": refresh_b})
    assert refresh_b_response.status_code == 401


def test_logout_empty_token_returns_401():
    """Une chaîne vide ou absente lève 422 (validation côté Pydantic)."""
    client, _, _ = create_environment()

    response = client.post("/auth/logout", json={"refresh_token": ""})
    assert response.status_code == 422  # Pydantic min_length=1
