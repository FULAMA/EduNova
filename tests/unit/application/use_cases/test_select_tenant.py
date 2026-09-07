from uuid import uuid4

import pytest

from src.application.use_cases.select_tenant import SelectTenant
from src.domain.entities.membership import Membership


class FakeMembershipRepository:

    def __init__(self, memberships):
        self.memberships = memberships

    def find_by_user_and_tenant(self, user_id, tenant_id):
        for membership in self.memberships:
            if (
                membership.user_id == user_id
                and membership.tenant_id == tenant_id
            ):
                return membership

        return None


def test_user_can_select_a_tenant_where_membership_is_active():
    user_id = uuid4()
    tenant_id = uuid4()

    membership = Membership(
        id=uuid4(),
        user_id=user_id,
        tenant_id=tenant_id,
        role="admin",
        active=True,
    )

    repository = FakeMembershipRepository([membership])
    use_case = SelectTenant(repository)

    context = use_case.execute(
        user_id=user_id,
        tenant_id=tenant_id,
    )

    assert context.tenant_id == tenant_id


def test_user_cannot_select_a_tenant_without_membership():
    user_id = uuid4()
    tenant_id = uuid4()

    repository = FakeMembershipRepository([])
    use_case = SelectTenant(repository)

    with pytest.raises(ValueError, match="tenant"):
        use_case.execute(
            user_id=user_id,
            tenant_id=tenant_id,
        )


def test_user_cannot_select_tenant_with_inactive_membership():
    user_id = uuid4()
    tenant_id = uuid4()

    membership = Membership(
        id=uuid4(),
        user_id=user_id,
        tenant_id=tenant_id,
        role="admin",
        active=False,
    )

    repository = FakeMembershipRepository([membership])
    use_case = SelectTenant(repository)

    with pytest.raises(ValueError, match="actif"):
        use_case.execute(
            user_id=user_id,
            tenant_id=tenant_id,
        )
def test_user_member_of_tenant_a_cannot_select_tenant_b():
    user_id = uuid4()
    tenant_a = uuid4()
    tenant_b = uuid4()

    membership_a = Membership(
        id=uuid4(),
        user_id=user_id,
        tenant_id=tenant_a,
        role="admin",
        active=True,
    )

    repository = FakeMembershipRepository([membership_a])
    use_case = SelectTenant(repository)

    with pytest.raises(ValueError, match="tenant"):
        use_case.execute(
            user_id=user_id,
            tenant_id=tenant_b,
        )
