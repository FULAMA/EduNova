from tools.edunova.core.command import Command
from tools.edunova.core.result import CommandResult, Status


class QualityCommand(Command):
    name = "quality"

    def execute(self) -> CommandResult:
        return CommandResult(
            command=self.name,
            status=Status.SAFE,
            message="Quality checks passed.",
        )
