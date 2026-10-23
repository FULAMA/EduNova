
from pathlib import Path

from tools.edunova.core.command import Command
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.cli_task_executor import run_cli_task
from tools.edunova.execution.service import AuditStatus
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.project_config import ProjectConfig, ProjectConfigError
from tools.edunova.security import redact_exception, redact_text


class SecurityCommand(Command):
    name = "security"

    def __init__(
        self,
        process_runner: ProcessRunner,
        project_config: ProjectConfig | None = None,
        audit_sink: ExecutionAuditSink | None = None,
    ) -> None:
        self._process_runner = process_runner
        self._project_config = project_config or ProjectConfig.load()
        self._audit_sink = audit_sink

    def execute(self) -> CommandResult:
        project_root = self._project_config.project_root
        try:
            targets = list(
                self._project_config.paths(
                    self._project_config.source_paths,
                    "source",
                )
            )
        except ProjectConfigError as error:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=redact_exception(error),
                exit_code=2,
            )

        if (project_root / "tools").is_dir() and not any(
            Path(target).parts[:1] == ("tools",)
            for target in targets
        ):
            targets.append("tools")

        if not targets:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message="No configured Python source directory exists.",
                exit_code=1,
            )

        try:
            execution = run_cli_task(
                self._process_runner,
                "bandit.scan",
                {"paths": targets, "options": self._project_config.bandit_args},
                project_root,
                audit_sink=self._audit_sink,
            )
        except FileNotFoundError as error:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=(
                    "Required executable was not found: "
                    f"{redact_text(error.filename or 'bandit')}"
                ),
                exit_code=127,
            )
        except OSError as error:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=f"Could not run security task: {redact_exception(error)}",
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
        audit_failed = execution.audit_status is AuditStatus.FAILED
        return CommandResult(
            command=self.name,
            status=(
                Status.REVIEW
                if audit_failed and result.returncode == 0
                else Status.SAFE
                if result.returncode == 0
                else Status.FAIL
            ),
            message=(
                "Bandit static analysis passed for Python source directories. "
                "Dependency vulnerabilities and manual security controls were "
                "not assessed."
                + (
                    " Execution audit unavailable."
                    if audit_failed
                    else ""
                )
            )
            if result.returncode == 0
            else redact_text(result.stdout.strip() or result.stderr.strip())
            + ("\nExecution audit unavailable." if audit_failed else ""),
            exit_code=result.returncode,
        )
