from uuid import uuid4
import pytest

from src.identity.application.dto.verify_login_two_factor_request import (
    VerifyLoginTwoFactorRequest,
)
from src.identity.application.use_cases.verify_login_two_factor import (
    VerifyLoginTwoFactor,
)
from src.identity.domain.entities.user import User
from src.identity.infrastructure.security.in_memory_rate_limiter import (
    InMemoryRateLimiter,
)
from src.infrastructure.security.jwt_service import JwtService
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID


class MockUserRepository:
    def __init__(self, user: User | None = None):
        self.user = user

    def find_by_id(self, user_id):
        if self.user and self.user.id == user_id:
            return self.user
        return None


class MockTenantRepository:
    def find_by_id(self, tenant_id):
        return Tenant(id=tenant_id, name="Test", slug="test", active=True)


class MockMembershipRepository:
    def find_by_user_and_tenant(self, user_id, tenant_id):
        return Membership(
            id=uuid4(),
            user_id=user_id,
            tenant_id=tenant_id,
            role="ADMIN",
            active=True,
        )


class MockTwoFactorService:
    def __init__(self, valid_code: str = "123456"):
        self.valid_code = valid_code

    def verify_code(self, secret: str, code: str) -> bool:
        return code == self.valid_code


def setup_env():
    user = User(
        id=uuid4(),
        email="totp-user@edunova.com",
        password_hash="hash",
        role="ADMIN",
        is_active=True,
        two_factor_enabled=True,
        two_factor_secret="JBSWY3DPEHPK3PXP",
    )
    jwt_service = JwtService(secret_key=TEST_JWT_SECRET)
    rate_limiter = InMemoryRateLimiter()
    two_factor_service = MockTwoFactorService(valid_code="123456")

    use_case = VerifyLoginTwoFactor(
        user_repository=MockUserRepository(user),
        membership_repository=MockMembershipRepository(),
        tenant_repository=MockTenantRepository(),
        two_factor_service=two_factor_service,
        jwt_service=jwt_service,
        rate_limiter=rate_limiter,
    )
    token = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
    return use_case, token, jwt_service, user


def test_totp_allows_valid_code_on_first_try():
    use_case, token, _, _ = setup_env()
    response = use_case.execute(
        VerifyLoginTwoFactorRequest(
            two_factor_token=token,
            code="123456",
        )
    )
    assert response.access_token
    assert response.refresh_token


def test_totp_blocks_after_three_failed_attempts():
    use_case, token, _, _ = setup_env()

    # Attempt 1 - wrong code
    with pytest.raises(ValueError, match="Code 2FA invalide"):
        use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token, code="000001")
        )

    # Attempt 2 - wrong code
    with pytest.raises(ValueError, match="Code 2FA invalide"):
        use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token, code="000002")
        )

    # Attempt 3 - wrong code
    with pytest.raises(ValueError, match="Code 2FA invalide"):
        use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token, code="000003")
        )

    # Attempt 4 - even with the RIGHT code, must be blocked with max attempts exceeded!
    with pytest.raises(ValueError, match="Nombre maximal de tentatives 2FA depasse"):
        use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token, code="123456")
        )


def test_totp_prevents_token_replay_after_success():
    use_case, token, _, _ = setup_env()

    # First consumption succeeds
    first = use_case.execute(
        VerifyLoginTwoFactorRequest(two_factor_token=token, code="123456")
    )
    assert first.access_token

    # Replay with same token is rejected
    with pytest.raises(ValueError, match="Token 2FA deja consomme"):
        use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token, code="123456")
        )


def test_totp_sessions_are_isolated():
    use_case, token1, jwt_service, user = setup_env()
    token2 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)

    # Exceed limits on token1
    for _ in range(3):
        with pytest.raises(ValueError):
            use_case.execute(
                VerifyLoginTwoFactorRequest(two_factor_token=token1, code="000000")
            )

    # token1 is blocked
    with pytest.raises(ValueError, match="Nombre maximal"):
        use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token1, code="123456")
        )

    # token2 is still fresh and succeeds!
    success = use_case.execute(
        VerifyLoginTwoFactorRequest(two_factor_token=token2, code="123456")
    )
    assert success.access_token
