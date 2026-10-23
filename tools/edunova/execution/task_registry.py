from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys
from types import MappingProxyType
from typing import Any

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.action_constraints import constraints_for
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.capability_matrix import allowed_capabilities
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope
from tools.edunova.infrastructure.tool_command import tool_command


class TaskValidationError(ValueError):
    """Raised when a registered task's request is outside its contract."""


ParameterValidator = Callable[[Mapping[str, Any], Path], dict[str, Any]]
CommandBuilder = Callable[[Mapping[str, Any], Path], tuple[str, ...]]
_RESOLUTION_SEAL = object()


@dataclass(frozen=True)
class ExecutionTask:
    task_id: str
    description: str
    action: ExecutionAction
    scopes: frozenset[ExecutionScope]
    capabilities: frozenset[ExecutionCapability]
    risk: ExecutionRisk
    validate_parameters: ParameterValidator
    build_command: CommandBuilder
    approval_required: bool = False
    expected_effects: str = "Run a bounded, read-only check."


@dataclass(frozen=True)
class ResolvedTask:
    task_id: str
    command: tuple[str, ...]
    project_root: Path
    parameter_digest: str
    parameters: Mapping[str, Any]
    _seal: object


def _require_keys(
    parameters: Mapping[str, Any],
    required: frozenset[str],
    optional: frozenset[str] = frozenset(),
) -> None:
    keys = set(parameters)
    if not required <= keys or keys - required - optional:
        raise TaskValidationError("Task parameters do not match its schema.")


def _safe_paths(values: Any, root: Path) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)) or not values:
        raise TaskValidationError("Task paths must be a non-empty list.")
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip() or "\x00" in value:
            raise TaskValidationError("Task paths must be non-empty strings.")
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise TaskValidationError("Task paths must stay inside the project.")
        resolved = (root / path).resolve()
        if not resolved.is_relative_to(root) or not resolved.exists():
            raise TaskValidationError("Task path is missing or outside the project.")
        normalized.append(resolved.relative_to(root).as_posix())
    return tuple(normalized)


def _safe_options(values: Any, task_id: str) -> tuple[str, ...]:
    if not isinstance(values, (list, tuple)) or any(
        not isinstance(value, str) or not value.strip() or "\x00" in value
        for value in values
    ):
        raise TaskValidationError("Task options must be non-empty strings.")
    options = tuple(values)
    if task_id == "pytest.run":
        index = 0
        while index < len(options):
            option = options[index]
            if option in {"-q", "-v", "-vv", "-x"}:
                index += 1
                continue
            if option.startswith("--maxfail="):
                value = option.split("=", 1)[1]
                if not value.isdecimal() or int(value) < 1:
                    raise TaskValidationError("Invalid pytest --maxfail value.")
            elif option == "--maxfail":
                index += 1
                if index >= len(options) or not options[index].isdecimal() or int(options[index]) < 1:
                    raise TaskValidationError("Invalid pytest --maxfail value.")
            elif option == "-k":
                index += 1
                if index >= len(options) or not all(
                    char.isalnum() or char in "_ -()"
                    for char in options[index]
                ):
                    raise TaskValidationError("Invalid pytest -k expression.")
            else:
                raise TaskValidationError("Pytest option is not allowed by this task.")
            index += 1
    elif task_id in {"ruff.check", "mypy.check"}:
        valued = (
            {"--select", "--ignore", "--line-length", "--target-version", "--output-format"}
            if task_id == "ruff.check"
            else {"--follow-imports"}
        )
        flags = (
            {"check"}
            if task_id == "ruff.check"
            else {"--strict", "--ignore-missing-imports", "--no-warn-return-any"}
        )
        index = 0
        while index < len(options):
            option = options[index]
            name, separator, attached = option.partition("=")
            if name in flags and not separator:
                index += 1
                continue
            if name not in valued:
                raise TaskValidationError(f"{task_id} option is not allowed by this task.")
            value = attached if separator else ""
            if not value and not separator:
                index += 1
                if index >= len(options):
                    raise TaskValidationError(f"{name} requires a value.")
                value = options[index]
            if not value or not all(char.isalnum() or char in "_,.-" for char in value):
                raise TaskValidationError(f"Invalid value for {name}.")
            if name == "--line-length" and not value.isdecimal():
                raise TaskValidationError("Ruff line length must be numeric.")
            index += 1
    elif task_id == "bandit.scan":
        if any(value not in {"-l", "-ll", "-lll", "-q", "-v"} for value in options):
            raise TaskValidationError("Bandit option is not allowed by this task.")
    return options


def _project_checks(task_id: str) -> tuple[ParameterValidator, CommandBuilder]:
    def validate(parameters: Mapping[str, Any], root: Path) -> dict[str, Any]:
        _require_keys(parameters, frozenset({"paths", "options"}))
        return {
            "paths": _safe_paths(parameters["paths"], root),
            "options": _safe_options(parameters["options"], task_id),
        }

    def build(parameters: Mapping[str, Any], root: Path) -> tuple[str, ...]:
        paths = tuple(parameters["paths"])
        options = tuple(parameters["options"])
        if task_id == "ruff.check":
            return tuple(tool_command("ruff", (*options, *paths)))
        if task_id == "mypy.check":
            return (sys.executable, "-m", "mypy", *paths, *options)
        return tuple(tool_command("bandit", ("-r", *paths, *options)))

    return validate, build


def _validate_pytest(parameters: Mapping[str, Any], root: Path) -> dict[str, Any]:
    _require_keys(parameters, frozenset({"paths", "options"}))
    return {
        "paths": _safe_paths(parameters["paths"], root),
        "options": _safe_options(parameters["options"], "pytest.run"),
    }


def _build_pytest(parameters: Mapping[str, Any], root: Path) -> tuple[str, ...]:
    base_temp = (root / ".pytest-work").resolve()
    if not base_temp.is_relative_to(root):
        raise TaskValidationError("Pytest temporary path escapes the project.")
    return (
        sys.executable,
        "-m",
        "pytest",
        "--basetemp",
        str(base_temp),
        *tuple(parameters["paths"]),
        *tuple(parameters["options"]),
    )


def _validate_git(parameters: Mapping[str, Any], root: Path) -> dict[str, Any]:
    del root
    _require_keys(parameters, frozenset({"untracked"}))
    if not isinstance(parameters["untracked"], bool):
        raise TaskValidationError("Git status untracked option must be boolean.")
    return {"untracked": parameters["untracked"]}


def _validate_git_branch(parameters: Mapping[str, Any], root: Path) -> dict[str, Any]:
    del root
    _require_keys(parameters, frozenset())
    return {}


class ExecutionTaskRegistry:
    """Explicit allowlist that validates task inputs before argv is built."""

    def __init__(self, tasks: tuple[ExecutionTask, ...] | None = None) -> None:
        self._tasks: dict[str, ExecutionTask] = {}
        for task in tasks if tasks is not None else self._builtins():
            self.register(task)

    def register(self, task: ExecutionTask) -> None:
        if not isinstance(task.task_id, str) or not re.fullmatch(
            r"[a-z][a-z0-9]*(?:\.[a-z][a-z0-9]*)+", task.task_id
        ):
            raise ValueError("Execution task id must be a stable dotted identifier.")
        if task.task_id in self._tasks:
            raise ValueError(f"Invalid or duplicate execution task: {task.task_id}")
        if task.risk > ExecutionRisk.MEDIUM and not task.approval_required:
            raise ValueError(
                "Elevated-risk tasks must require explicit local confirmation."
            )
        if (
            task.action in {
                ExecutionAction.MODIFY,
                ExecutionAction.DELETE,
                ExecutionAction.INSTALL,
                ExecutionAction.MIGRATE,
                ExecutionAction.GIT_COMMIT,
                ExecutionAction.GIT_PUSH,
            }
            and not task.approval_required
        ):
            raise ValueError("Sensitive task actions must require local confirmation.")
        if not task.description.strip() or not task.scopes or not task.capabilities:
            raise ValueError("Execution tasks require description, scope, and capabilities.")
        constraints = constraints_for(task.action)
        if (
            task.action is ExecutionAction.SHELL
            or not task.scopes <= constraints.scopes
            or task.risk > constraints.max_risk
            or not task.capabilities <= allowed_capabilities(task.action)
            or ExecutionCapability.PROCESS_EXECUTE not in task.capabilities
        ):
            raise ValueError("Execution task exceeds its action's allowed contract.")
        self._tasks[task.task_id] = task

    def get(self, task_id: str) -> ExecutionTask:
        if not isinstance(task_id, str):
            raise TaskValidationError("Execution task id must be a string.")
        try:
            return self._tasks[task_id]
        except KeyError as error:
            raise TaskValidationError(f"Unknown execution task: {task_id}") from error

    def resolve(
        self,
        task_id: str,
        parameters: Mapping[str, Any],
        project_root: Path,
    ) -> ResolvedTask:
        task = self.get(task_id)
        root = project_root.resolve(strict=True)
        if not root.is_dir():
            raise TaskValidationError("Project root must be a directory.")
        validated = task.validate_parameters(parameters, root)
        command = task.build_command(validated, root)
        if not command or any(not part or "\x00" in part for part in command):
            raise TaskValidationError("Task produced an invalid process command.")
        digest = hashlib.sha256(
            json.dumps(validated, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return ResolvedTask(
            task_id,
            tuple(command),
            root,
            digest,
            MappingProxyType(validated),
            _RESOLUTION_SEAL,
        )

    @staticmethod
    def _builtins() -> tuple[ExecutionTask, ...]:
        fs = ExecutionCapability.FILESYSTEM_READ
        process = ExecutionCapability.PROCESS_EXECUTE
        git = ExecutionCapability.GIT_READ
        test_validator, test_builder = _project_checks("pytest.run")
        ruff_validator, ruff_builder = _project_checks("ruff.check")
        mypy_validator, mypy_builder = _project_checks("mypy.check")
        bandit_validator, bandit_builder = _project_checks("bandit.scan")
        return (
            ExecutionTask("pytest.run", "Run the configured test suite", ExecutionAction.TEST, frozenset({ExecutionScope.TEST_SUITE, ExecutionScope.PROJECT}), frozenset({fs, process}), ExecutionRisk.MEDIUM, test_validator, _build_pytest),
            ExecutionTask("ruff.check", "Run Ruff checks", ExecutionAction.QUALITY, frozenset({ExecutionScope.PROJECT}), frozenset({fs, process}), ExecutionRisk.MEDIUM, ruff_validator, ruff_builder),
            ExecutionTask("mypy.check", "Run Mypy checks", ExecutionAction.QUALITY, frozenset({ExecutionScope.PROJECT}), frozenset({fs, process}), ExecutionRisk.MEDIUM, mypy_validator, mypy_builder),
            ExecutionTask("bandit.scan", "Run Bandit static analysis", ExecutionAction.SECURITY, frozenset({ExecutionScope.PROJECT, ExecutionScope.TEST_SUITE}), frozenset({fs, process}), ExecutionRisk.MEDIUM, bandit_validator, bandit_builder),
            ExecutionTask("git.status", "Read Git working tree status", ExecutionAction.SCAN, frozenset({ExecutionScope.GIT}), frozenset({fs, git, process}), ExecutionRisk.LOW, _validate_git, lambda p, _r: ("git", "status", "--short", *(("--untracked-files=all",) if p["untracked"] else ()))),
            ExecutionTask("git.branch", "Read current Git branch", ExecutionAction.SCAN, frozenset({ExecutionScope.GIT}), frozenset({fs, git, process}), ExecutionRisk.LOW, _validate_git_branch, lambda _p, _r: ("git", "branch", "--show-current")),
        )

def is_registry_resolved(task: object) -> bool:
    return isinstance(task, ResolvedTask) and task._seal is _RESOLUTION_SEAL
