from uuid import uuid4

import pytest

from src.infrastructure.security.jwt_service import (
    JwtService,
)


TEST_SECRET = "edunova-test-secret-key-32-bytes-minimum"


def test_create_two_factor_token_contains_pending_type():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()
    tenant_id = uuid4()

    token = service.create_two_factor_token(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    payload = service.decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["tenant_id"] == str(tenant_id)
    assert payload["type"] == "2fa_pending"


def test_two_factor_token_is_different_from_access_token():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()
    tenant_id = uuid4()

    access_token = service.create_access_token(
        user_id=user_id,
        role="ADMIN",
        tenant_id=tenant_id,
    )

    two_factor_token = service.create_two_factor_token(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    assert access_token != two_factor_token

