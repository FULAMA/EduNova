from uuid import uuid4

import pytest

from src.application.services.jwt_service import JwtService


JWT_SECRET = "edunova-test-secret-key-32-bytes-minimum"


def test_decode_refresh_token_accepts_refresh_token():
    service = JwtService(secret_key=JWT_SECRET)
    user_id = uuid4()

    token = service.create_refresh_token(user_id)

    payload = service.decode_refresh_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_decode_refresh_token_rejects_access_token():
    service = JwtService(secret_key=JWT_SECRET)

    token = service.create_access_token(
        user_id=uuid4(),
        role="ADMIN",
    )

    with pytest.raises(ValueError, match="Token refresh requis"):
        service.decode_refresh_token(token)


def test_decode_refresh_token_rejects_two_factor_token():
    service = JwtService(secret_key=JWT_SECRET)

    token = service.create_two_factor_token(uuid4())

    with pytest.raises(ValueError, match="Token refresh requis"):
        service.decode_refresh_token(token)


def test_decode_refresh_token_rejects_invalid_token():
    service = JwtService(secret_key=JWT_SECRET)

    with pytest.raises(ValueError, match="Token JWT invalide"):
        service.decode_refresh_token("token-invalide")


def test_decode_refresh_token_rejects_empty_token():
    service = JwtService(secret_key=JWT_SECRET)

    with pytest.raises(ValueError):
        service.decode_refresh_token("")
