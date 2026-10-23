from dataclasses import dataclass, field
from pathlib import Path

from tools.edunova.execution.action import ExecutionAction
from tools.edunova.execution.capability import ExecutionCapability
from tools.edunova.execution.risk import ExecutionRisk
from tools.edunova.execution.scope import ExecutionScope


@dataclass(frozen=True)
class ExecutionRequest:
    action: ExecutionAction
    target: str
    scope: ExecutionScope
    actor: str
    risk: ExecutionRisk
    requested_capabilities: frozenset[ExecutionCapability]
    evidence: tuple[str, ...] = ()
    context: tuple[str, ...] = ()
    project_root: Path = field(default_factory=Path.cwd)

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise ValueError("Execution target cannot be empty.")

        if not self.actor.strip():
            raise ValueError("Execution actor cannot be empty.")
