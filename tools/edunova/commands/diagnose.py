from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import subprocess
from typing import Sequence

from tools.edunova.commands.quality import QualityCommand
from tools.edunova.commands.run_tests import RunTestsCommand
from tools.edunova.commands.security import SecurityCommand
from tools.edunova.core.command import Command
from tools.edunova.core.result import CommandResult, Status
from tools.edunova.execution.cli_task_executor import run_cli_task
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.service import AuditStatus
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.project_config import ProjectConfig
from tools.edunova.security import redact_exception, redact_text


class DiagnosticStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    REVIEW_REQUIRED = "REVIEW REQUIRED"


@dataclass(frozen=True)
class DiagnosticStep:
    name: str
    status: DiagnosticStatus
    message: str
    exit_code: int


class GitChangesCommand(Command):
    """Read the working tree summary without changing Git state."""

    name = "git_changes"

    def __init__(
        self,
        process_runner: ProcessRunner,
        project_config: ProjectConfig,
        audit_sink: ExecutionAuditSink | None = None,
    ) -> None:
        self._process_runner = process_runner
        self._project_config = project_config
        self._audit_sink = audit_sink

    def execute(self) -> CommandResult:
        try:
            execution = run_cli_task(
                self._process_runner,
                "git.status",
                {"untracked": True},
                self._project_config.project_root,
                audit_sink=self._audit_sink,
            )
        except FileNotFoundError as error:
            executable = error.filename or "git"
            return CommandResult(
                command=self.name,
                status=Status.REVIEW,
                message=(
                    "Git summary unavailable; executable not found: "
                    f"{redact_text(executable)}"
                ),
                exit_code=127,
            )
        except OSError as error:
            return CommandResult(
                command=self.name,
                status=Status.REVIEW,
                message=f"Git summary unavailable: {redact_exception(error)}",
                exit_code=2,
            )
        if not execution.executed or execution.process is None:
            return CommandResult(
                command=self.name,
                status=Status.REVIEW,
                message="Git status was not executed: " + execution.decision.reason,
                exit_code=2,
            )

        result = execution.process
        if result.returncode != 0:
            details = redact_text(result.stderr.strip() or result.stdout.strip())
            message = f"git status returned exit code {result.returncode}."
            if details:
                message = f"{message} {details}"
            return CommandResult(
                command=self.name,
                status=Status.REVIEW,
                message=message,
                exit_code=result.returncode,
            )

        lines = [line for line in result.stdout.splitlines() if line]
        counts = {"modified": 0, "added": 0, "deleted": 0, "untracked": 0}
        for line in lines:
            code = line[:2]
            if code == "??":
                counts["untracked"] += 1
            elif "D" in code:
                counts["deleted"] += 1
            elif "A" in code or "R" in code or "C" in code:
                counts["added"] += 1
            else:
                counts["modified"] += 1

        if not lines:
            summary = "No changed files reported by git status."
        else:
            summary = (
                f"{len(lines)} changed path(s): "
                f"{counts['modified']} modified, {counts['added']} added, "
                f"{counts['deleted']} deleted, "
                f"{counts['untracked']} untracked."
            )
            summary += "\n" + "\n".join(f"  {line}" for line in lines)

        if execution.audit_status is AuditStatus.FAILED:
            return CommandResult(
                command=self.name,
                status=Status.REVIEW,
                message="Git status completed, but execution audit failed.",
                exit_code=2,
            )

        return CommandResult(
            command=self.name,
            status=Status.SAFE,
            message=summary,
        )


class DiagnoseCommand(Command):
    """Run existing project checks and report each result independently."""

    name = "diagnose"

    def __init__(
        self,
        process_runner: ProcessRunner,
        project_config: ProjectConfig,
        commands: Sequence[tuple[str, Command]] | None = None,
        audit_sink: ExecutionAuditSink | None = None,
    ) -> None:
        self._commands = tuple(
            commands
            or (
                (
                    "Tests",
                    RunTestsCommand(process_runner, project_config, audit_sink),
                ),
                (
                    "Quality (Ruff + Mypy)",
                    QualityCommand(
                        process_runner,
                        project_config,
                        include_tests=False,
                        audit_sink=audit_sink,
                    ),
                ),
                (
                    "Bandit security scan",
                    SecurityCommand(process_runner, project_config, audit_sink),
                ),
                (
                    "Git working tree",
                    GitChangesCommand(process_runner, project_config, audit_sink),
                ),
            )
        )

    def execute(self) -> CommandResult:
        steps: list[DiagnosticStep] = []
        interrupted = False

        for index, (name, command) in enumerate(self._commands):
            try:
                result = command.execute()
            except KeyboardInterrupt:
                result = CommandResult(
                    command=command.name,
                    status=Status.FAIL,
                    message="Interrupted by user.",
                    exit_code=130,
                )
                steps.append(self._step(name, result))
                for remaining_name, _ in self._commands[index + 1 :]:
                    steps.append(
                        DiagnosticStep(
                            remaining_name,
                            DiagnosticStatus.SKIPPED,
                            "Skipped because the diagnostic was interrupted.",
                            130,
                        )
                    )
                interrupted = True
                break
            except subprocess.TimeoutExpired as error:
                result = CommandResult(
                    command=command.name,
                    status=Status.FAIL,
                    message=f"Timed out: {redact_exception(error)}",
                    exit_code=124,
                )
            except FileNotFoundError as error:
                missing = error.filename or "required executable"
                result = CommandResult(
                    command=command.name,
                    status=Status.FAIL,
                    message=f"Required executable was not found: {missing}",
                    exit_code=127,
                )
            except OSError as error:
                result = CommandResult(
                    command=command.name,
                    status=Status.FAIL,
                    message=f"Could not run step: {redact_exception(error)}",
                    exit_code=126,
                )
            except Exception as error:
                result = CommandResult(
                    command=command.name,
                    status=Status.FAIL,
                    message=(
                        "Unexpected step error "
                        f"({type(error).__name__}): {redact_text(str(error))}"
                    ),
                    exit_code=1,
                )

            steps.append(self._step(name, result))

        overall, exit_code = self._overall(steps, interrupted)
        report = ["FulamaWorkflow project diagnostic"]
        for step in steps:
            report.append(
                f"{step.name}: {step.status.value} (exit {step.exit_code})"
            )
            if step.message:
                report.extend(f"  {line}" for line in step.message.splitlines())
        report.append(f"Overall: {overall.value} (exit {exit_code})")

        return CommandResult(
            command=self.name,
            status=(
                Status.FAIL
                if overall is DiagnosticStatus.FAILED
                else Status.REVIEW
                if overall is DiagnosticStatus.REVIEW_REQUIRED
                else Status.SAFE
            ),
            message="\n".join(report),
            exit_code=exit_code,
        )

    @staticmethod
    def _step(name: str, result: CommandResult) -> DiagnosticStep:
        if result.status is Status.FAIL or (
            result.status is Status.SAFE and result.exit_code != 0
        ):
            status = DiagnosticStatus.FAILED
            exit_code = result.exit_code or 1
        elif result.status in {Status.REVIEW, Status.WARN}:
            status = DiagnosticStatus.REVIEW_REQUIRED
            exit_code = result.exit_code
        else:
            status = DiagnosticStatus.SUCCEEDED
            exit_code = result.exit_code
        return DiagnosticStep(name, status, result.message, exit_code)

    @staticmethod
    def _overall(
        steps: Sequence[DiagnosticStep], interrupted: bool
    ) -> tuple[DiagnosticStatus, int]:
        if interrupted:
            return DiagnosticStatus.FAILED, 130
        failed = [step for step in steps if step.status is DiagnosticStatus.FAILED]
        if failed:
            return DiagnosticStatus.FAILED, next(
                (step.exit_code for step in failed if step.exit_code), 1
            )
        if any(step.status is DiagnosticStatus.REVIEW_REQUIRED for step in steps):
            return DiagnosticStatus.REVIEW_REQUIRED, 2
        return DiagnosticStatus.SUCCEEDED, 0
