from sqlite3 import Connection


version = "041"


def upgrade(connection: Connection) -> None:
    connection.execute("CREATE TABLE IF NOT EXISTS school_profile_audit (id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, actor_user_id TEXT NOT NULL, action TEXT NOT NULL, before_state TEXT, after_state TEXT NOT NULL, occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE RESTRICT)")
    connection.execute("CREATE INDEX IF NOT EXISTS ix_school_profile_audit_tenant_time ON school_profile_audit (tenant_id, occurred_at, id)")
    connection.execute("CREATE TRIGGER IF NOT EXISTS trg_school_profile_audit_no_update BEFORE UPDATE ON school_profile_audit BEGIN SELECT RAISE(ABORT, 'audit records are immutable'); END")
    connection.execute("CREATE TRIGGER IF NOT EXISTS trg_school_profile_audit_no_delete BEFORE DELETE ON school_profile_audit BEGIN SELECT RAISE(ABORT, 'audit records are immutable'); END")
