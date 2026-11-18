from uuid import uuid4
import pytest

from src.identity.application.dto.login_user_request import LoginUserRequest
from src.identity.application.use_cases.login_user import (
    LoginUser,
    _DUMMY_ARGON2_HASH,
)
from src.identity.domain.entities.user import User
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant
from tests.support.tenant import TEST_TENANT_ID


class SpyPasswordHasher:
    def __init__(self):
        self.verified_hashes: list[str] = []

    def hash(self, password: str) -> str:
        return "hashed-password"

    def verify(self, password: str, password_hash: str) -> bool:
        self.verified_hashes.append(password_hash)
        return password_hash == "valid-hash"


class MockUserRepository:
    def __init__(self, user: User | None = None):
        self.user = user

    def find_by_email(self, email: str) -> User | None:
        if self.user and self.user.email == email:
            return self.user
        return None

    def find_by_id(self, user_id):
        if self.user and self.user.id == user_id:
            return self.user
        return None

    def save(self, user):
        self.user = user


class MockTenantRepository:
    def find_by_id(self, tenant_id):
        return Tenant(
            id=tenant_id,
            name="Test",
            slug="test",
            active=True,
        )


class MockMembershipRepository:
    def find_by_user_and_tenant(self, user_id, tenant_id):
        return Membership(
            id=uuid4(),
            user_id=user_id,
            tenant_id=tenant_id,
            role="ADMIN",
            active=True,
        )


class MockJwtService:
    def create_access_token(self, user_id, role, tenant_id):
        return "access"

    def create_refresh_token(self, user_id, tenant_id):
        return "refresh"

    def create_two_factor_token(self, user_id, tenant_id):
        return "2fa"


def test_non_existent_user_invokes_dummy_hash_verification():
    hasher = SpyPasswordHasher()
    use_case = LoginUser(
        user_repository=MockUserRepository(user=None),
        membership_repository=MockMembershipRepository(),
        tenant_repository=MockTenantRepository(),
        password_hasher=hasher,
        two_factor_service=None,  # type: ignore
        jwt_service=MockJwtService(),
    )

    with pytest.raises(ValueError) as exc_info:
        use_case.execute(
            LoginUserRequest(
                email="unknown@edunova.com",
                password="AnyPassword123!",
                tenant_id=TEST_TENANT_ID,
            )
        )

    # Error message must be generic to prevent enumeration
    assert str(exc_info.value) == "Identifiants invalides."
    # The dummy hash must have been verified to equalize execution timing
    assert _DUMMY_ARGON2_HASH in hasher.verified_hashes


def test_inactive_and_deactivated_user_returns_uniform_error():
    user = User(
        id=uuid4(),
        email="inactive@edunova.com",
        password_hash="valid-hash",
        role="ADMIN",
        is_active=False,
    )
    hasher = SpyPasswordHasher()
    use_case = LoginUser(
        user_repository=MockUserRepository(user=user),
        membership_repository=MockMembershipRepository(),
        tenant_repository=MockTenantRepository(),
        password_hasher=hasher,
        two_factor_service=None,  # type: ignore
        jwt_service=MockJwtService(),
    )

    with pytest.raises(ValueError) as exc_info:
        use_case.execute(
            LoginUserRequest(
                email="inactive@edunova.com",
                password="AnyPassword123!",
                tenant_id=TEST_TENANT_ID,
            )
        )

    # Identical message to wrong password and non-existent account
    assert str(exc_info.value) == "Identifiants invalides."
    # Password verification must still run to avoid timing shortcut
    assert "valid-hash" in hasher.verified_hashes


def test_wrong_password_returns_uniform_error():
    user = User(
        id=uuid4(),
        email="active@edunova.com",
        password_hash="different-hash",
        role="ADMIN",
        is_active=True,
    )
    hasher = SpyPasswordHasher()
    use_case = LoginUser(
        user_repository=MockUserRepository(user=user),
        membership_repository=MockMembershipRepository(),
        tenant_repository=MockTenantRepository(),
        password_hasher=hasher,
        two_factor_service=None,  # type: ignore
        jwt_service=MockJwtService(),
    )

    with pytest.raises(ValueError) as exc_info:
        use_case.execute(
            LoginUserRequest(
                email="active@edunova.com",
                password="WrongPassword!",
                tenant_id=TEST_TENANT_ID,
            )
        )

    assert str(exc_info.value) == "Identifiants invalides."
    assert "different-hash" in hasher.verified_hashes
