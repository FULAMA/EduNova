import importlib
import pkgutil
import sqlite3
from datetime import datetime, timezone
from typing import Callable

from .migration import Migration


MigrationFunction = Callable[[sqlite3.Connection], None]


class MigrationRunner:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection
        self._migrations: dict[str, MigrationFunction] = {}

    def register(
        self,
        version_or_migration: str | Migration,
        migration: MigrationFunction | None = None,
    ) -> None:
        if isinstance(version_or_migration, Migration):
            self._migrations[version_or_migration.version] = (
                version_or_migration.upgrade
            )
            return

        if migration is None:
            raise TypeError(
                "Une fonction de migration est obligatoire."
            )

        self._migrations[version_or_migration] = migration

    def register_module(self, module) -> None:
        self.register(
            Migration(
                version=module.version,
                upgrade=module.upgrade,
            )
        )

    def discover(self, package_name: str) -> None:
        package = importlib.import_module(package_name)

        for module_info in pkgutil.iter_modules(
            package.__path__,
            package.__name__ + ".",
        ):
            if module_info.name.rsplit(".", 1)[-1].startswith("_"):
                continue

            module = importlib.import_module(module_info.name)

            if hasattr(module, "version") and hasattr(module, "upgrade"):
                self.register_module(module)
    def run(self) -> None:
        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
        """)

        for version in sorted(self._migrations):
            already_applied = self._connection.execute("""
                SELECT 1
                FROM schema_migrations
                WHERE version = ?
            """, (version,)).fetchone()

            if already_applied is not None:
                continue

            self._migrations[version](self._connection)

            self._connection.execute("""
                INSERT INTO schema_migrations (version, applied_at)
                VALUES (?, ?)
            """, (
                version,
                datetime.now(timezone.utc).isoformat(),
            ))

        self._connection.commit()





