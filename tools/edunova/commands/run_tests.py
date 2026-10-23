from tools.edunova.core.command import Command
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.cli_task_executor import run_cli_task
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.execution.service import AuditStatus
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.project_config import ProjectConfig, ProjectConfigError
from tools.edunova.security import redact_exception, redact_text


class RunTestsCommand(Command):
    name = "run_tests"

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
        base_temp = project_root / ".pytest-work"

        try:
            test_paths = self._project_config.paths(
                self._project_config.test_paths,
                "test",
            )
        except ProjectConfigError as error:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=redact_exception(error),
                exit_code=2,
            )

        base_temp.mkdir(parents=True, exist_ok=True)

        try:
            execution = run_cli_task(
                self._process_runner,
                "pytest.run",
                {"paths": test_paths, "options": self._project_config.pytest_args},
                project_root,
                audit_sink=self._audit_sink,
            )
        except PermissionError as error:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=redact_exception(error),
                exit_code=126,
            )

        if not execution.executed or execution.process is None:
            return CommandResult(
                command=self.name,
                status=Status.FAIL,
                message=execution.decision.reason,
                exit_code=126,
            )

        result = execution.process

        status = (
            Status.SAFE
            if result.returncode == 0
            else Status.FAIL
        )

        message = redact_text(result.stdout.strip() or result.stderr.strip())
        if execution.audit_status is AuditStatus.FAILED:
            message = f"{message}\nExecution audit unavailable.".strip()
            if status is Status.SAFE:
                status = Status.REVIEW

        return CommandResult(
            command=self.name,
            status=status,
            message=message,
            exit_code=result.returncode,
        )
