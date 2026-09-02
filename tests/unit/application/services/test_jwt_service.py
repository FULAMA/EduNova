from uuid import uuid4

import pytest

from src.application.services.jwt_service import (
    JwtService,
)


TEST_SECRET = "edunova-test-secret-key-32-bytes-minimum"


def test_create_access_token_returns_string():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()

    token = service.create_access_token(
        user_id=user_id,
        role="ADMIN",
    )

    assert isinstance(token, str)
    assert token


def test_access_token_contains_user_id_and_role():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()

    token = service.create_access_token(
        user_id=user_id,
        role="ADMIN",
    )

    payload = service.decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "ADMIN"
    assert payload["type"] == "access"


def test_decode_invalid_token_raises_value_error():
    service = JwtService(secret_key=TEST_SECRET)

    with pytest.raises(ValueError):
        service.decode_token("invalid-token")


def test_token_created_with_different_secret_is_rejected():
    service_one = JwtService(
        secret_key="edunova-secret-one-32-bytes-minimum"
    )
    service_two = JwtService(
        secret_key="edunova-secret-two-32-bytes-minimum"
    )

    user_id = uuid4()

    token = service_one.create_access_token(
        user_id=user_id,
        role="ADMIN",
    )

    with pytest.raises(ValueError):
        service_two.decode_token(token)


def test_create_refresh_token_contains_refresh_type():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()

    token = service.create_refresh_token(
        user_id=user_id,
    )

    payload = service.decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_empty_secret_key_is_rejected():
    with pytest.raises(ValueError):
        JwtService(secret_key="")


def test_access_and_refresh_tokens_are_different():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()

    access_token = service.create_access_token(
        user_id=user_id,
        role="ADMIN",
    )

    refresh_token = service.create_refresh_token(
        user_id=user_id,
    )

    assert access_token != refresh_token
