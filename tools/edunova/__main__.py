import sys

from tools.edunova.agents.orchestration.service import AgentOrchestrationService
from tools.edunova.cli import main as cli_main
from tools.edunova.execution.sqlite_audit_sink import (
    AuditStorageError,
    SqliteExecutionAuditSink,
)
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.project_config import ProjectConfig, ProjectConfigError


def _create_agent_service() -> AgentOrchestrationService:
    from tools.edunova.composition import create_agent_service

    return create_agent_service()


def main(
    args: list[str] | None = None,
    process_runner: ProcessRunner | None = None,
    agent_service: AgentOrchestrationService | None = None,
) -> int:
    command_args = sys.argv[1:] if args is None else args

    if command_args and command_args[0] in {"agent", "agent-orchestrated"}:
        if len(command_args) == 2 and command_args[1] in {"--help", "-h"}:
            return cli_main(command_args)
        if len(command_args) != 2 or not command_args[1].strip():
            print("Agent task is required.")
            return 1
        if agent_service is None:
            try:
                agent_service = _create_agent_service()
            except ImportError:
                print(
                    "Agent provider SDKs are missing. Install the optional "
                    "'agents' dependencies to enable agent commands."
                )
                return 1
            except Exception as error:
                print(
                    "Agent service could not be initialized "
                    f"({type(error).__name__})."
                )
                return 1

    audit_sink = None
    if (
        command_args
        and command_args[0] not in {"--help", "-h"}
        and not (
            len(command_args) == 2
            and command_args[1] in {"--help", "-h"}
        )
    ):
        try:
            project_config = ProjectConfig.load()
            audit_sink = SqliteExecutionAuditSink(
                project_config.audit_database_path()
            )
        except (AuditStorageError, ProjectConfigError, ValueError):
            print("Audit storage could not be initialized.")
            return 2

    return cli_main(
        command_args,
        process_runner=process_runner,
        agent_service=agent_service,
        audit_sink=audit_sink,
    )


if __name__ == "__main__":
    raise SystemExit(main())
