from tools.edunova.agents.orchestration.service import AgentOrchestrationService
import subprocess

from tools.edunova.bootstrap import CliBootstrap
from tools.edunova.execution.audit_sink import ExecutionAuditSink
from tools.edunova.infrastructure.process_runner import ProcessRunner
from tools.edunova.project_config import ProjectConfigError
from tools.edunova.security import redact_exception, redact_text


def _print_help(bootstrap: CliBootstrap) -> None:
    print("EduNova CLI")
    print()
    print("Usage:")
    print("  edunova <command> [arguments]")
    print("  python -m tools.edunova <command> [arguments]")
    print()
    print("Commands:")

    names = list(bootstrap.registry.names())

    for optional_name in ("agent", "agent-orchestrated"):
        if optional_name not in names:
            names.append(optional_name)

    for name in names:
        print(f"  {name}")


def _print_command_help(bootstrap: CliBootstrap, name: str) -> None:
    print(f"EduNova command: {name}")
    if name in {"agent", "agent-orchestrated"}:
        print(f"Usage: edunova {name} <task>")
    else:
        print(f"Usage: edunova {name}")
    print("This command has no additional command-line options.")


def main(
    args: list[str],
    process_runner: ProcessRunner | None = None,
    agent_service: AgentOrchestrationService | None = None,
    audit_sink: ExecutionAuditSink | None = None,
) -> int:
    try:
        if agent_service is None:
            if audit_sink is None:
                bootstrap = CliBootstrap(process_runner=process_runner)
            else:
                bootstrap = CliBootstrap(
                    process_runner=process_runner,
                    audit_sink=audit_sink,
                )
        else:
            if audit_sink is None:
                bootstrap = CliBootstrap(
                    process_runner=process_runner,
                    agent_service=agent_service,
                )
            else:
                bootstrap = CliBootstrap(
                    process_runner=process_runner,
                    agent_service=agent_service,
                    audit_sink=audit_sink,
                )
    except ProjectConfigError as error:
        print(f"Invalid [tool.edunova] configuration: {redact_exception(error)}")
        return 2

    if not args:
        _print_help(bootstrap)
        return 0

    if args[0] in {"--help", "-h"}:
        _print_help(bootstrap)
        return 0

    if (
        len(args) == 2
        and args[1] in {"--help", "-h"}
        and (
            bootstrap.registry.has(args[0])
            or args[0] in {"agent", "agent-orchestrated"}
        )
    ):
        _print_command_help(bootstrap, args[0])
        return 0

    try:
        result = bootstrap.dispatcher.dispatch(
            args[0],
            args[1:],
        )
    except KeyError:
        print(f"Unknown command: {redact_text(args[0])}")
        print("Use --help to list available commands.")
        return 1
    except ValueError as error:
        print(f"Command could not run: {redact_exception(error)}")
        return 1
    except FileNotFoundError as error:
        executable = error.filename or "required executable"
        print(
            f"Command could not start: {redact_text(executable)} was not found."
        )
        return 127
    except subprocess.TimeoutExpired as error:
        print(f"Command timed out: {redact_text(str(error.cmd))}")
        return 124
    except KeyboardInterrupt:
        print("Command interrupted.")
        return 130
    except OSError as error:
        print(f"Command could not start: {redact_exception(error)}")
        return 126
    except Exception as error:
        # Do not print exception details: providers and subprocesses may include secrets.
        print(f"Command failed unexpectedly ({type(error).__name__}).")
        return 1

    message = getattr(result, "message", None)

    if message:
        print(redact_text(message))

    return result.exit_code
