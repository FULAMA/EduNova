from uuid import uuid4
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from src.identity.application.use_cases.login_user import LoginUserResponse
from src.identity.application.use_cases.register_user import RegisterUserResponse as AppRegisterResponse
from src.identity.infrastructure.security.in_memory_rate_limiter import InMemoryRateLimiter
from src.presentation.api.routes.auth import (
    login_user,
    register_user,
    verify_login_two_factor,
)
from src.presentation.api.schemas.login_user_request import LoginUserRequest
from src.presentation.api.schemas.register_user_request import RegisterUserRequest
from src.presentation.api.schemas.verify_login_two_factor_request import (
    VerifyLoginTwoFactorRequest,
)
from tests.support.tenant import TEST_TENANT_ID


def build_mock_http_request(ip: str = "192.168.1.100"):
    request = MagicMock()
    request.headers = {}
    request.client.host = ip
    return request


def test_login_rate_limiting_per_ip():
    rate_limiter = InMemoryRateLimiter()
    http_request = build_mock_http_request(ip="10.0.0.1")
    use_case = MagicMock()
    use_case.execute.side_effect = ValueError("Identifiants invalides.")

    request = LoginUserRequest(
        email="user@edunova.com",
        password="badpassword",
        tenant_id=TEST_TENANT_ID,
    )

    # First 5 calls fail with 401
    for _ in range(5):
        with pytest.raises(HTTPException) as exc_info:
            login_user(request, http_request, use_case, rate_limiter)
        assert exc_info.value.status_code == 401

    # 6th call hits the per-(IP, target) limit (5 attempts) -> HTTP 429
    with pytest.raises(HTTPException) as exc_info:
        login_user(request, http_request, use_case, rate_limiter)

    assert exc_info.value.status_code == 429
    assert "Trop de tentatives" in exc_info.value.detail
    assert "Retry-After" in exc_info.value.headers
    # Ensure no passwords or sensitive internals leaked
    assert "password" not in exc_info.value.detail.lower()


def test_login_rate_limiting_does_not_lock_out_victim_on_different_ip():
    rate_limiter = InMemoryRateLimiter()
    attacker_request = build_mock_http_request(ip="198.51.100.1")
    victim_request = build_mock_http_request(ip="203.0.113.42")

    use_case = MagicMock()
    use_case.execute.side_effect = ValueError("Identifiants invalides.")

    login_req = LoginUserRequest(
        email="victim@edunova.com",
        password="badpassword",
        tenant_id=TEST_TENANT_ID,
    )

    # Attacker tries 5 times and gets blocked
    for _ in range(5):
        with pytest.raises(HTTPException):
            login_user(login_req, attacker_request, use_case, rate_limiter)

    with pytest.raises(HTTPException) as exc_info:
        login_user(login_req, attacker_request, use_case, rate_limiter)
    assert exc_info.value.status_code == 429

    # Legitimate user on different IP is NOT blocked
    # When entering correct password, login succeeds!
    use_case.execute.side_effect = None
    use_case.execute.return_value = LoginUserResponse(
        authenticated=True,
        two_factor_required=False,
        two_factor_token=None,
        access_token="valid-token",
        refresh_token="valid-refresh",
        email="victim@edunova.com",
    )
    result = login_user(login_req, victim_request, use_case, rate_limiter)
    assert result.authenticated is True


def test_login_successful_resets_target_counter():
    rate_limiter = InMemoryRateLimiter()
    http_request = build_mock_http_request(ip="10.0.0.2")
    use_case = MagicMock()

    login_req = LoginUserRequest(
        email="user@edunova.com",
        password="testpassword",
        tenant_id=TEST_TENANT_ID,
    )

    # 4 failed attempts
    use_case.execute.side_effect = ValueError("Identifiants invalides.")
    for _ in range(4):
        with pytest.raises(HTTPException):
            login_user(login_req, http_request, use_case, rate_limiter)

    # 5th attempt succeeds
    use_case.execute.side_effect = None
    use_case.execute.return_value = LoginUserResponse(
        authenticated=True,
        two_factor_required=False,
        two_factor_token=None,
        access_token="token",
        refresh_token="refresh",
        email="user@edunova.com",
    )
    res = login_user(login_req, http_request, use_case, rate_limiter)
    assert res.authenticated is True

    # Counter should be reset: immediate failed attempt is allowed again (not blocked by 429)
    use_case.execute.side_effect = ValueError("Identifiants invalides.")
    with pytest.raises(HTTPException) as exc_info:
        login_user(login_req, http_request, use_case, rate_limiter)
    assert exc_info.value.status_code == 401  # Not 429!


def test_register_rate_limiting_blocks_after_five_attempts():
    rate_limiter = InMemoryRateLimiter()
    http_request = build_mock_http_request(ip="10.0.0.3")
    use_case = MagicMock()
    use_case.execute.return_value = AppRegisterResponse(
        id=uuid4(),
        email="new@edunova.com",
        role="STUDENT",
        is_active=True,
        two_factor_enabled=False,
    )

    req = RegisterUserRequest(
        email="new@edunova.com",
        password="SecretPassword123!",
    )

    # 5 successful registrations
    for _ in range(5):
        register_user(req, http_request, use_case, rate_limiter)

    # 6th registration from same IP is rate limited
    with pytest.raises(HTTPException) as exc_info:
        register_user(req, http_request, use_case, rate_limiter)

    assert exc_info.value.status_code == 429
    assert "Trop de tentatives d inscription" in exc_info.value.detail
    assert "Retry-After" in exc_info.value.headers


def test_verify_2fa_rate_limiting_ip():
    rate_limiter = InMemoryRateLimiter()
    http_request = build_mock_http_request(ip="10.0.0.4")
    use_case = MagicMock()
    use_case.execute.side_effect = ValueError("Code 2FA invalide.")

    req = VerifyLoginTwoFactorRequest(
        two_factor_token="fake-2fa-token",
        code="123456",
    )

    # 10 attempts
    for _ in range(10):
        with pytest.raises(HTTPException):
            verify_login_two_factor(req, http_request, use_case, rate_limiter)

    # 11th attempt hits IP limit
    with pytest.raises(HTTPException) as exc_info:
        verify_login_two_factor(req, http_request, use_case, rate_limiter)

    assert exc_info.value.status_code == 429
    assert "Trop de tentatives 2FA" in exc_info.value.detail
