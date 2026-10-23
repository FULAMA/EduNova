from pathlib import Path

from tools.edunova.agents.context import EngineeringContext, GitChange
from tools.edunova.execution.cli_task_executor import run_cli_task
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.execution.service import AuditStatus
from tools.edunova.infrastructure.process_runner import ProcessRunner


class ContextScanner:
    def __init__(
        self,
        project_root: Path,
        scope: str,
        process_runner: ProcessRunner,
        audit_sink: ExecutionAuditSink | None = None,
    ) -> None:
        self._project_root = project_root
        self._scope = scope
        self._process_runner = process_runner
        self._audit_sink = audit_sink

    def scan(self) -> EngineeringContext:
        branch_execution = run_cli_task(
            self._process_runner,
            "git.branch",
            {},
            self._project_root,
            audit_sink=self._audit_sink,
        )

        status_execution = run_cli_task(
            self._process_runner,
            "git.status",
            {"untracked": False},
            self._project_root,
            audit_sink=self._audit_sink,
        )

        if not branch_execution.executed or branch_execution.process is None:
            raise PermissionError(branch_execution.decision.reason)
        if not status_execution.executed or status_execution.process is None:
            raise PermissionError(status_execution.decision.reason)

        branch_result = branch_execution.process
        status_result = status_execution.process
        risks: list[str] = []

        if branch_execution.audit_status is AuditStatus.FAILED:
            risks.append("Git branch scan audit unavailable.")
        if status_execution.audit_status is AuditStatus.FAILED:
            risks.append("Git status scan audit unavailable.")

        if branch_result.returncode != 0:
            risks.append(
                "Git branch scan failed: "
                f"{branch_result.stderr.strip() or 'unknown error'}"
            )

        if status_result.returncode != 0:
            risks.append(
                "Git status scan failed: "
                f"{status_result.stderr.strip() or 'unknown error'}"
            )

        branch = (
            branch_result.stdout.strip()
            if branch_result.returncode == 0
            else ""
        )

        git_status = self._parse_status(
            status_result.stdout
            if status_result.returncode == 0
            else ""
        )

        git_changes = self._parse_git_changes(git_status)
        changed_files = tuple(change.path for change in git_changes)

        architecture = self._discover_architecture(risks)
        tests = self._discover_tests(risks)

        return EngineeringContext(
            project_root=self._project_root,
            scope=self._scope,
            git_branch=branch,
            git_status=git_status,
            git_changes=git_changes,
            changed_files=changed_files,
            architecture=architecture,
            tests=tests,
            risks=tuple(risks),
        )

    def _discover_architecture(self, risks: list[str]) -> tuple[str, ...]:
        discovered: list[str] = []

        roots = (
            self._project_root / "src",
            self._project_root / "tools" / "edunova",
        )

        for root in roots:
            if not root.is_dir():
                continue

            try:
                children = sorted(
                    child
                    for child in root.iterdir()
                    if child.is_dir()
                    and child.name != "__pycache__"
                    and not child.name.startswith(".")
                )
            except OSError as exc:
                risks.append(
                    f"Architecture scan failed for {root}: {exc}"
                )
                continue

            for child in children:
                discovered.append(
                    child.relative_to(self._project_root).as_posix()
                )

        return tuple(discovered)

    def _discover_tests(self, risks: list[str]) -> tuple[str, ...]:
        tests_root = self._project_root / "tests"

        if not tests_root.is_dir():
            return ()

        discovered: list[str] = []

        try:
            children = sorted(
                child
                for child in tests_root.iterdir()
                if child.is_dir()
                and child.name != "__pycache__"
                and not child.name.startswith(".")
            )
        except OSError as exc:
            risks.append(
                f"Tests scan failed for {tests_root}: {exc}"
            )
            return ()

        for child in children:
            discovered.append(
                child.relative_to(self._project_root).as_posix()
            )

        return tuple(discovered)

    @staticmethod
    def _parse_status(output: str) -> tuple[str, ...]:
        return tuple(
            line
            for line in output.splitlines()
            if line.strip()
        )

    @staticmethod
    def _parse_git_changes(
        git_status: tuple[str, ...],
    ) -> tuple[GitChange, ...]:
        changes: list[GitChange] = []

        for entry in git_status:
            if len(entry) < 3:
                continue

            status = entry[:2]
            path = entry[3:].strip()

            if not path:
                continue

            changes.append(
                GitChange(
                    status=status,
                    path=path,
                )
            )

        return tuple(changes)
