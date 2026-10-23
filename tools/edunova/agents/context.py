from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitChange:
    status: str
    path: str


@dataclass(frozen=True)
class EngineeringContext:
    project_root: Path
    scope: str
    git_branch: str = ""
    git_status: tuple[str, ...] = ()
    git_changes: tuple[GitChange, ...] = ()
    changed_files: tuple[str, ...] = ()
    architecture: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    decisions: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
