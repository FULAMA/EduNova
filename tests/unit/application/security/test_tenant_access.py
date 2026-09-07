from uuid import uuid4

import pytest

from src.application.security.tenant_access import TenantAccess


def test_tenant_access_allows_same_tenant():
    tenant_id = uuid4()

    access = TenantAccess(tenant_id)

    assert access.allows(tenant_id) is True


def test_tenant_access_rejects_another_tenant():
    tenant_a = uuid4()
    tenant_b = uuid4()

    access = TenantAccess(tenant_a)

    assert access.allows(tenant_b) is False


def test_tenant_access_requires_a_tenant():
    with pytest.raises(ValueError, match="tenant"):
        TenantAccess(None)
