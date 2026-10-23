from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any


class ProjectConfigError(ValueError):
    """Raised when the project's EduNova CLI configuration is invalid."""


@dataclass(frozen=True)
class ProjectConfig:
    project_root: Path
    source_paths: tuple[str, ...] = ("src",)
    test_paths: tuple[str, ...] = ("tests",)
    ruff_args: tuple[str, ...] = ("check",)
    mypy_args: tuple[str, ...] = ()
    pytest_args: tuple[str, ...] = ()
    bandit_args: tuple[str, ...] = ("-ll",)
    timeout_seconds: float = 600
    audit_path: str = ".edunova/audit.sqlite3"

    @classmethod
    def load(cls, start: Path | None = None) -> ProjectConfig:
        root = cls._find_project_root(start or Path.cwd())
        config_file = root / "pyproject.toml"
        if not config_file.is_file():
            return cls(project_root=root)

        try:
            with config_file.open("rb") as file:
                document = tomllib.load(file)
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
            raise ProjectConfigError(
                f"Cannot read {config_file}: {error}"
            ) from error

        tool = document.get("tool", {})
        section = tool.get("edunova", {}) if isinstance(tool, dict) else None
        if section is None:
            return cls(project_root=root)
        if not isinstance(section, dict):
            raise ProjectConfigError("[tool.edunova] must be a TOML table.")

        allowed_keys = {
            "source_paths",
            "test_paths",
            "timeout_seconds",
            "commands",
            "audit_path",
        }
        cls._reject_unknown(section, allowed_keys, "[tool.edunova]")

        commands = section.get("commands", {})
        if not isinstance(commands, dict):
            raise ProjectConfigError(
                "[tool.edunova.commands] must be a TOML table."
            )
        cls._reject_unknown(
            commands,
            {"ruff_args", "mypy_args", "pytest_args", "bandit_args"},
            "[tool.edunova.commands]",
        )

        timeout = section.get("timeout_seconds", 600)
        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or timeout <= 0
        ):
            raise ProjectConfigError(
                "timeout_seconds must be a positive number."
            )

        audit_path = section.get("audit_path", ".edunova/audit.sqlite3")
        audit_candidate = Path(audit_path) if isinstance(audit_path, str) else None
        if (
            audit_candidate is None
            or not audit_path.strip()
            or audit_candidate.is_absolute()
            or ".." in audit_candidate.parts
            or "\x00" in audit_path
        ):
            raise ProjectConfigError(
                "audit_path must be a non-empty relative path."
            )

        pytest_args = cls._string_list(
            commands.get("pytest_args", []),
            "commands.pytest_args",
            allow_empty=True,
        )
        cls._validate_pytest_args(pytest_args)

        return cls(
            project_root=root,
            source_paths=cls._string_list(
                section.get("source_paths", ["src"]),
                "source_paths",
            ),
            test_paths=cls._string_list(
                section.get("test_paths", ["tests"]),
                "test_paths",
            ),
            ruff_args=cls._string_list(
                commands.get("ruff_args", ["check"]),
                "commands.ruff_args",
                allow_empty=True,
            ),
            mypy_args=cls._string_list(
                commands.get("mypy_args", []),
                "commands.mypy_args",
                allow_empty=True,
            ),
            pytest_args=pytest_args,
            bandit_args=cls._string_list(
                commands.get("bandit_args", ["-ll"]),
                "commands.bandit_args",
                allow_empty=True,
            ),
            timeout_seconds=float(timeout),
            audit_path=audit_path,
        )

    def audit_database_path(self) -> Path:
        root = self.project_root.resolve()
        candidate = (root / self.audit_path).resolve()
        if not candidate.is_relative_to(root):
            raise ProjectConfigError(
                "audit_path must stay relative to the project root."
            )
        return candidate

    def paths(self, values: tuple[str, ...], label: str) -> tuple[str, ...]:
        resolved: list[str] = []
        root = self.project_root.resolve()
        for value in values:
            candidate = (root / value).resolve()
            if not candidate.is_relative_to(root):
                raise ProjectConfigError(
                    f"Configured {label} path escapes the project root: {value}"
                )
            if not candidate.exists():
                raise ProjectConfigError(
                    f"Configured {label} path does not exist: {value}"
                )
            resolved.append(candidate.relative_to(root).as_posix())
        return tuple(resolved)

    @staticmethod
    def _find_project_root(start: Path) -> Path:
        anchor = start.resolve()
        if anchor.is_file():
            anchor = anchor.parent
        for candidate in (anchor, *anchor.parents):
            if (candidate / "pyproject.toml").is_file():
                return candidate
        return anchor

    @staticmethod
    def _reject_unknown(
        table: dict[str, Any],
        allowed: set[str],
        label: str,
    ) -> None:
        unknown = sorted(set(table) - allowed)
        if unknown:
            raise ProjectConfigError(
                f"Unknown {label} option(s): {', '.join(unknown)}."
            )

    @staticmethod
    def _string_list(
        value: Any,
        label: str,
        *,
        allow_empty: bool = False,
    ) -> tuple[str, ...]:
        if (
            not isinstance(value, list)
            or (not value and not allow_empty)
            or any(not isinstance(item, str) or not item.strip() for item in value)
        ):
            qualifier = "a list of non-empty strings"
            if allow_empty:
                qualifier = "a list of non-empty strings (or an empty list)"
            raise ProjectConfigError(f"{label} must be {qualifier}.")

        if label in {"source_paths", "test_paths"}:
            for item in value:
                if "\x00" in item:
                    raise ProjectConfigError(
                        f"{label} cannot contain NUL characters."
                    )
                path = Path(item)
                if path.is_absolute() or ".." in path.parts:
                    raise ProjectConfigError(
                        f"{label} entries must stay relative to the project root: {item}"
                    )
        elif any("\x00" in item for item in value):
            raise ProjectConfigError(f"{label} cannot contain NUL characters.")

        return tuple(value)

    @staticmethod
    def _validate_pytest_args(arguments: tuple[str, ...]) -> None:
        protected = {"--basetemp", "-c", "--rootdir"}
        for argument in arguments:
            option = argument.split("=", 1)[0]
            if option in protected:
                raise ProjectConfigError(
                    f"commands.pytest_args cannot override {option}; "
                    "the CLI controls pytest's project and temporary roots."
                )
