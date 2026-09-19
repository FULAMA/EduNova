from uuid import UUID

TEST_TENANT_ID = UUID("00000000-0000-0000-0000-000000000001")


def seed_tenant(container, tenant_id=TEST_TENANT_ID, active=True):
    with container._database.connect() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO tenants (id, name, slug, active) VALUES (?, ?, ?, ?)",
            (str(tenant_id), f"Tenant {tenant_id}", f"tenant-{tenant_id}", int(active)),
        )
    return tenant_id


def seed_membership(container, user_id, tenant_id=TEST_TENANT_ID, *, active=True, role="ADMIN"):
    from uuid import uuid4

    seed_tenant(container, tenant_id)
    with container._database.connect() as connection:
        connection.execute(
            "INSERT INTO memberships (id, user_id, tenant_id, role, active) VALUES (?, ?, ?, ?, ?)",
            (str(uuid4()), str(user_id), str(tenant_id), role, int(active)),
        )
