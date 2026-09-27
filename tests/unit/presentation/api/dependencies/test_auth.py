import pytest
from uuid import uuid4

from src.identity.domain.entities.user import User
from src.tenancy.domain.entities.membership import Membership
from src.presentation.api.dependencies.auth import require_role
from src.shared.application.context.tenant_context import TenantContext


class FakeMembershipRepository:
    def __init__(self, membership=None):
        self.membership = membership

    def find_by_user_and_tenant(self, user_id, tenant_id):
        if self.membership is None:
            return None

        if (
            self.membership.user_id == user_id
            and self.membership.tenant_id == tenant_id
        ):
            return self.membership

        return None


class FakeContainer:
    def __init__(self, membership_repository):
        self._repository = membership_repository

    def _membership_repository(self):
        return self._repository


def build_user(role="ADMIN"):
    return User(
        id=uuid4(),
        email="user@edunova.com",
        password_hash="hashed-password",
        role=role,
    )


def build_context():
    tenant_id = uuid4()
    return TenantContext(tenant_id=tenant_id)


def build_container(user, tenant_context, role):
    membership = Membership(
        id=uuid4(),
        user_id=user.id,
        tenant_id=tenant_context.tenant_id,
        role=role,
        active=True,
    )

    repository = FakeMembershipRepository(membership)

    return FakeContainer(repository)


def test_require_role_allows_expected_role():
    user = build_user("ADMIN")
    tenant_context = build_context()
    membership_repository = build_container(
        user,
        tenant_context,
        "ADMIN",
    )._membership_repository()

    dependency = require_role("ADMIN")

    assert dependency(
        current_user=user,
        tenant_context=tenant_context,
        membership_repository=membership_repository,
    ) == user


def test_require_role_rejects_wrong_role():
    user = build_user("TEACHER")
    tenant_context = build_context()
    membership_repository = build_container(
        user,
        tenant_context,
        "TEACHER",
    )._membership_repository()

    dependency = require_role("ADMIN")

    with pytest.raises(Exception):
        dependency(
            current_user=user,
            tenant_context=tenant_context,
            membership_repository=membership_repository,
        )


def test_require_role_rejects_empty_roles():
    with pytest.raises(ValueError):
        require_role()


def test_require_role_accepts_multiple_roles():
    user = build_user("TEACHER")
    tenant_context = build_context()
    membership_repository = build_container(
        user,
        tenant_context,
        "TEACHER",
    )._membership_repository()

    dependency = require_role("ADMIN", "TEACHER")

    assert dependency(
        current_user=user,
        tenant_context=tenant_context,
        membership_repository=membership_repository,
    ) == user



