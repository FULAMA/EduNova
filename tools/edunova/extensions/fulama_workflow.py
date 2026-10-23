from collections.abc import Sequence

from tools.edunova.commands.work import WorkCommand
from tools.edunova.core.command import Command
from tools.edunova.core.command_registry import CommandRegistry


class FulamaWorkflow(WorkCommand):
    """Named reusable alias for the current fail-fast work workflow.

    It intentionally adds no business behavior until a separate Fulama
    contract is defined.
    """

    name = "fulama-workflow"

    def __init__(self, steps: Sequence[Command]) -> None:
        if not steps:
            raise ValueError("FulamaWorkflow requires at least one step.")

        super().__init__(steps)

    @classmethod
    def register(
        cls,
        registry: CommandRegistry,
        steps: Sequence[Command],
    ) -> "FulamaWorkflow":
        """Create and register the workflow in an existing CLI registry."""
        workflow = cls(steps)
        registry.register(workflow)
        return workflow
