from dataclasses import dataclass
from typing import Sequence

from tools.edunova.core.command import Command
from tools.edunova.core.result import CommandResult, Status


@dataclass(frozen=True)
class WorkResult:
    results: tuple[CommandResult, ...]
    status: Status

    @property
    def succeeded(self) -> bool:
        return self.status is Status.SAFE


class WorkCommand(Command):
    name = "work"

    def __init__(self, commands: Sequence[Command]) -> None:
        self._commands = tuple(commands)

    def execute(self) -> CommandResult:
        result = self.run_workflow()

        return CommandResult(
            command=self.name,
            status=result.status,
            message=self._build_message(result),
        )

    def run_workflow(self) -> WorkResult:
        results: list[CommandResult] = []

        for command in self._commands:
            try:
                result = command.execute()
            except Exception as error:
                result = CommandResult(
                    command=command.name,
                    status=Status.FAIL,
                    message=(
                        f"Workflow step '{command.name}' failed "
                        f"unexpectedly ({type(error).__name__})."
                    ),
                )
            results.append(result)

            if result.status == Status.FAIL:
                return WorkResult(
                    results=tuple(results),
                    status=Status.FAIL,
                )

        status = self._resolve_status(results)

        return WorkResult(
            results=tuple(results),
            status=status,
        )

    @staticmethod
    def _resolve_status(results: list[CommandResult]) -> Status:
        if any(result.status == Status.REVIEW for result in results):
            return Status.REVIEW

        if any(result.status == Status.WARN for result in results):
            return Status.WARN

        return Status.SAFE

    @staticmethod
    def _build_message(result: WorkResult) -> str:
        executed = len(result.results)

        if result.status == Status.FAIL:
            return f"Workflow stopped after {executed} command(s)."

        return (
            f"Workflow completed with status "
            f"{result.status.value} after {executed} command(s)."
        )
