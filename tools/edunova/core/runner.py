from .command import Command
from .result import CommandResult


class CommandRunner:
    def run(self, command: Command) -> CommandResult:
        return command.execute()
