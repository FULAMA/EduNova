from uuid import uuid4

import pytest

from src.application.context.tenant_context import TenantContext


def test_tenant_context_requires_a_tenant():
    with pytest.raises(ValueError, match="tenant"):
        TenantContext(None)


def test_tenant_context_stores_tenant_id():
    tenant_id = uuid4()

    context = TenantContext(tenant_id)

    assert context.tenant_id == tenant_id
