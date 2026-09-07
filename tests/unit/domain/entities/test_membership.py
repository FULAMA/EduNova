from uuid import UUID, uuid4

import pytest

from src.domain.entities.membership import Membership


def test_membership_can_be_created():
    user_id = uuid4()
    tenant_id = uuid4()

    membership = Membership(
        id=uuid4(),
        user_id=user_id,
        tenant_id=tenant_id,
        role="admin",
    )

    assert isinstance(membership.id, UUID)
    assert membership.user_id == user_id
    assert membership.tenant_id == tenant_id
    assert membership.role == "admin"
    assert membership.active is True


def test_membership_role_cannot_be_empty():
    with pytest.raises(ValueError, match="role"):
        Membership(
            id=uuid4(),
            user_id=uuid4(),
            tenant_id=uuid4(),
            role="   ",
        )
