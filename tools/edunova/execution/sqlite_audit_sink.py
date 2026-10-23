from __future__ import annotations

from datetime import datetime, timezone
from contextlib import contextmanager
import json
from pathlib import Path
import os
import sqlite3

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.audit import ExecutionAuditRecord
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.decision import ExecutionDecisionType
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope
from tools.edunova.security import redact_text


class AuditStorageError(RuntimeError):
    """Raised when audit storage cannot safely read or write an event."""


class SqliteExecutionAuditSink(ExecutionAuditSink):
    """Durable audit sink with transactional, serialized SQLite writes."""

    def __init__(self, path: Path, *, retention_limit: int | None = None) -> None:
        if retention_limit is not None and retention_limit < 1:
            raise ValueError("retention_limit must be positive.")

        self._path = path.resolve()
        self._retention_limit = retention_limit
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            if self._path.exists() and not self._path.is_file():
                raise AuditStorageError("Audit storage path is not a file.")
            with self._connection() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS audit_events (
                        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TEXT NOT NULL,
                        payload TEXT NOT NULL CHECK (json_valid(payload))
                    )
                    """
                )
            self._restrict_permissions()
        except AuditStorageError:
            raise
        except (OSError, sqlite3.Error):
            raise AuditStorageError("Audit storage is unavailable.") from None

    def record(self, audit: ExecutionAuditRecord) -> None:
        payload = json.dumps(
            self._serialize(audit),
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        try:
            with self._connection() as connection:
                connection.execute(
                    "INSERT INTO audit_events (created_at, payload) VALUES (?, ?)",
                    (datetime.now(timezone.utc).isoformat(), payload),
                )
                if self._retention_limit is not None:
                    connection.execute(
                        """
                        DELETE FROM audit_events
                        WHERE event_id NOT IN (
                            SELECT event_id FROM audit_events
                            ORDER BY event_id DESC LIMIT ?
                        )
                        """,
                        (self._retention_limit,),
                    )
        except (OSError, sqlite3.Error):
            raise AuditStorageError("Audit storage is unavailable.") from None

    @property
    def records(self) -> tuple[ExecutionAuditRecord, ...]:
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    "SELECT payload FROM audit_events ORDER BY event_id"
                ).fetchall()
        except (OSError, sqlite3.Error):
            raise AuditStorageError("Audit storage is unavailable.") from None

        try:
            return tuple(self._deserialize(row[0]) for row in rows)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            raise AuditStorageError("Audit storage is corrupt.") from None

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path, timeout=5.0)
        connection.execute("PRAGMA busy_timeout = 5000")
        connection.execute("PRAGMA synchronous = FULL")
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _restrict_permissions(self) -> None:
        if os.name != "nt":
            self._path.chmod(0o600)

    @staticmethod
    def _serialize(audit: ExecutionAuditRecord) -> dict[str, object]:
        return {
            "action": audit.action.value,
            "target": redact_text(audit.target),
            "scope": audit.scope.value,
            "actor": redact_text(audit.actor),
            "risk": audit.risk.name,
            "requested_capabilities": sorted(
                capability.value for capability in audit.requested_capabilities
            ),
            "evidence": [redact_text(item) for item in audit.evidence],
            "decision": audit.decision.value,
            "reason": redact_text(audit.reason),
            "policy": redact_text(audit.policy),
            "required_approval": audit.required_approval,
            "executed": audit.executed,
            "exit_code": audit.exit_code,
            "attempted": audit.attempted,
            "failure": redact_text(audit.failure) if audit.failure else None,
            "task_id": audit.task_id,
            "parameter_digest": audit.parameter_digest,
        }

    @staticmethod
    def _deserialize(payload: str) -> ExecutionAuditRecord:
        data = json.loads(payload)
        data["action"] = ExecutionAction(data["action"])
        data["scope"] = ExecutionScope(data["scope"])
        data["risk"] = ExecutionRisk[data["risk"]]
        data["requested_capabilities"] = frozenset(
            ExecutionCapability(value)
            for value in data["requested_capabilities"]
        )
        data["evidence"] = tuple(data["evidence"])
        data["decision"] = ExecutionDecisionType(data["decision"])
        return ExecutionAuditRecord(**data)
