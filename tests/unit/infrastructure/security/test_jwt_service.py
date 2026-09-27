from uuid import uuid4

import pytest

from src.infrastructure.security.jwt_service import (
    JwtService,
)


TEST_SECRET = "edunova-test-secret-key-32-bytes-minimum"


def test_create_access_token_returns_string():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()
    tenant_id = uuid4()

    token = service.create_access_token(
        user_id=user_id,
        role="ADMIN",
        tenant_id=tenant_id,
    )

    assert isinstance(token, str)
    assert token


def test_access_token_contains_user_id_and_role():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()
    tenant_id = uuid4()

    token = service.create_access_token(
        user_id=user_id,
        role="ADMIN",
        tenant_id=tenant_id,
    )

    payload = service.decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["role"] == "ADMIN"
    assert payload["tenant_id"] == str(tenant_id)
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
    tenant_id = uuid4()

    token = service_one.create_access_token(
        user_id=user_id,
        role="ADMIN",
        tenant_id=tenant_id,
    )

    with pytest.raises(ValueError):
        service_two.decode_token(token)


def test_create_refresh_token_contains_refresh_type():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()
    tenant_id = uuid4()

    token = service.create_refresh_token(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    payload = service.decode_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["tenant_id"] == str(tenant_id)
    assert payload["type"] == "refresh"


def test_empty_secret_key_is_rejected():
    with pytest.raises(ValueError):
        JwtService(secret_key="")


def test_access_and_refresh_tokens_are_different():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()
    tenant_id = uuid4()

    access_token = service.create_access_token(
        user_id=user_id,
        role="ADMIN",
        tenant_id=tenant_id,
    )

    refresh_token = service.create_refresh_token(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    assert access_token != refresh_token


def test_create_two_factor_token_contains_expected_claims():
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


def test_decode_token_rejects_empty_token():
    service = JwtService(secret_key=TEST_SECRET)

    with pytest.raises(ValueError, match="token ne peut pas etre vide"):
        service.decode_token("")


def test_decode_refresh_token_rejects_non_refresh_token():
    service = JwtService(secret_key=TEST_SECRET)

    token = service.create_access_token(
        user_id=uuid4(),
        role="ADMIN",
        tenant_id=uuid4(),
    )

    with pytest.raises(ValueError, match="Token refresh requis"):
        service.decode_refresh_token(token)


def test_decode_refresh_token_rejects_missing_jti():
    service = JwtService(secret_key=TEST_SECRET)

    import jwt

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "tenant_id": str(uuid4()),
            "type": "refresh",
        },
        TEST_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(
        ValueError,
        match="token refresh ne contient pas de jti",
    ):
        service.decode_refresh_token(token)


def test_decode_refresh_token_rejects_missing_tenant():
    service = JwtService(secret_key=TEST_SECRET)

    import jwt

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "jti": str(uuid4()),
            "type": "refresh",
        },
        TEST_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(
        ValueError,
        match="token refresh ne contient pas de tenant",
    ):
        service.decode_refresh_token(token)


def test_decode_refresh_token_rejects_missing_user():
    service = JwtService(secret_key=TEST_SECRET)

    import jwt

    token = jwt.encode(
        {
            "jti": str(uuid4()),
            "tenant_id": str(uuid4()),
            "type": "refresh",
        },
        TEST_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(
        ValueError,
        match="token refresh ne contient pas d utilisateur",
    ):
        service.decode_refresh_token(token)


def test_decode_refresh_token_returns_valid_payload():
    service = JwtService(secret_key=TEST_SECRET)

    token = service.create_refresh_token(
        user_id=uuid4(),
        tenant_id=uuid4(),
    )

    payload = service.decode_refresh_token(token)

    assert payload["type"] == "refresh"
    assert payload["sub"]
    assert payload["jti"]
    assert payload["tenant_id"]
def test_jwt_service_rejects_invalid_access_token_expiration():
    with pytest.raises(ValueError):
        JwtService(
            secret_key=TEST_SECRET,
            access_token_expire_minutes=0,
        )

    with pytest.raises(ValueError):
        JwtService(
            secret_key=TEST_SECRET,
            access_token_expire_minutes=-1,
        )


def test_jwt_service_rejects_invalid_refresh_token_expiration():
    with pytest.raises(ValueError):
        JwtService(
            secret_key=TEST_SECRET,
            refresh_token_expire_days=0,
        )

    with pytest.raises(ValueError):
        JwtService(
            secret_key=TEST_SECRET,
            refresh_token_expire_days=-1,
        )


def test_jwt_tokens_have_expiration_claim():
    service = JwtService(secret_key=TEST_SECRET)

    user_id = uuid4()
    tenant_id = uuid4()

    access_payload = service.decode_token(
        service.create_access_token(
            user_id=user_id,
            role="ADMIN",
            tenant_id=tenant_id,
        )
    )

    refresh_payload = service.decode_token(
        service.create_refresh_token(
            user_id=user_id,
            tenant_id=tenant_id,
        )
    )

    two_factor_payload = service.decode_token(
        service.create_two_factor_token(
            user_id=user_id,
            tenant_id=tenant_id,
        )
    )

    assert access_payload["exp"] > access_payload["iat"]
    assert refresh_payload["exp"] > refresh_payload["iat"]
    assert two_factor_payload["exp"] > two_factor_payload["iat"]
def test_decode_token_rejects_expired_token():
    import jwt
    from datetime import datetime, timedelta, timezone

    service = JwtService(secret_key=TEST_SECRET)

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "tenant_id": str(uuid4()),
            "type": "access",
            "iat": datetime.now(timezone.utc) - timedelta(minutes=10),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        TEST_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Token JWT invalide"):
        service.decode_token(token)
def test_decode_token_rejects_token_with_future_iat():
    import jwt
    from datetime import datetime, timedelta, timezone

    service = JwtService(secret_key=TEST_SECRET)

    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "tenant_id": str(uuid4()),
            "type": "access",
            "iat": datetime.now(timezone.utc) + timedelta(minutes=10),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
        },
        TEST_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(ValueError):
        service.decode_token(token)
def test_jwt_service_rejects_short_secret_key():
    with pytest.raises(ValueError):
        JwtService(secret_key="abc")

def test_create_refresh_tokens_have_unique_jti():
    service = JwtService(
        secret_key="a" * 32,
    )

    token_1 = service.create_refresh_token(
        user_id=uuid4(),
        tenant_id=uuid4(),
    )

    token_2 = service.create_refresh_token(
        user_id=uuid4(),
        tenant_id=uuid4(),
    )

    payload_1 = service.decode_refresh_token(token_1)
    payload_2 = service.decode_refresh_token(token_2)

    assert payload_1["jti"] != payload_2["jti"]

