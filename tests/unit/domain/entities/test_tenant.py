from uuid import UUID, uuid4

import pytest

from src.tenancy.domain.entities.tenant import Tenant


def test_tenant_can_be_created():
    tenant = Tenant(
        id=uuid4(),
        name="Institut Nzambe",
        slug="institut-nzambe",
    )

    assert isinstance(tenant.id, UUID)
    assert tenant.name == "Institut Nzambe"
    assert tenant.slug == "institut-nzambe"
    assert tenant.active is True


def test_tenant_name_cannot_be_empty():
    with pytest.raises(ValueError, match="nom"):
        Tenant(
            id=uuid4(),
            name="   ",
            slug="institut-nzambe",
        )


def test_tenant_slug_cannot_be_empty():
    with pytest.raises(ValueError, match="slug"):
        Tenant(
            id=uuid4(),
            name="Institut Nzambe",
            slug="   ",
        )
