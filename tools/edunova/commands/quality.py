from pathlib import Path

from tools.edunova.core.command import Command
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.cli_task_executor import run_cli_task
from tools.edunova.execution.service import AuditStatus
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.project_config import ProjectConfig, ProjectConfigError
from tools.edunova.security import redact_exception, redact_text


class QualityCommand(Command):
    name = "quality"

    def __init__(
        self,
        process_runner: ProcessRunner,
        project_config: ProjectConfig | None = None,
        *,
        include_tests: bool = True,
        audit_sink: ExecutionAuditSink | None = None,
    ) -> None:
        self._process_runner = process_runner
        self._project_config = project_config or ProjectConfig.load()
        self._include_tests = include_tests
        self._audit_sink = audit_sink

    def execute(self) -> CommandResult:
        project_root = Path(self._project_config.project_root)
        base_temp = project_root / ".pytest-work"

        try:
            source_paths = self._project_config.paths(
                self._project_config.source_paths,
                "source",
            )
            test_paths = (
                self._project_config.paths(
                    self._project_config.test_paths,
                    "test",
                )
                if self._include_tests
                else ()
            )
        except ProjectConfigError as error:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=redact_exception(error),
                exit_code=2,
            )

        if self._include_tests:
            base_temp.mkdir(parents=True, exist_ok=True)

        checks: list[tuple[str, dict[str, object]]] = [
            ("ruff.check", {"paths": source_paths, "options": self._project_config.ruff_args}),
            ("mypy.check", {"paths": source_paths, "options": self._project_config.mypy_args}),
        ]
        if self._include_tests:
            checks.append(("pytest.run", {"paths": test_paths, "options": self._project_config.pytest_args}))

        for task_id, parameters in checks:
            try:
                execution = run_cli_task(
                    self._process_runner,
                    task_id,
                    parameters,
                    project_root,
                    audit_sink=self._audit_sink,
                )
            except FileNotFoundError as error:
                return CommandResult(
                    command=self.name,
                    status=Status.FAIL,
                    message=(
                        "Required executable was not found: "
                        f"{redact_text(error.filename or 'tool')}"
                    ),
                    exit_code=127,
                )
            except OSError as error:
                return CommandResult(
                    command=self.name,
                    status=Status.FAIL,
                    message=f"Could not run quality task: {redact_exception(error)}",
                    exit_code=126,
                )
            except (PermissionError, ValueError) as error:
                return CommandResult(
                    command=self.name,
                    status=Status.FAIL,
                    message=redact_exception(error),
                    exit_code=2,
                )

            if not execution.executed or execution.process is None:
                return CommandResult(
                    command=self.name,
                    status=Status.FAIL,
                    message=execution.decision.reason,
                    exit_code=126,
                )

            result = execution.process
            if result.returncode != 0:
                message = redact_text(result.stdout.strip() or result.stderr.strip())
                if execution.audit_status is AuditStatus.FAILED:
                    message = f"{message}\nExecution audit unavailable."

                return CommandResult(
                    command=self.name,
                    status=Status.FAIL,
                    message=message,
                    exit_code=result.returncode,
                )

            if execution.audit_status is AuditStatus.FAILED:
                return CommandResult(
                    command=self.name,
                    status=Status.REVIEW,
                    message="Quality task completed, but execution audit failed.",
                )

        return CommandResult(
            command=self.name,
            status=Status.SAFE,
            message="Quality checks passed.",
        )
