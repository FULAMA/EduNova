from pathlib import Path

from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_builder import ContextBuilder


class FakeContextScanner:
    def __init__(self, context: EngineeringContext) -> None:
        self.context = context
        self.calls = 0

    def scan(self) -> EngineeringContext:
        self.calls += 1
        return self.context


def test_context_builder_returns_scanned_context() -> None:
    expected = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="academic-records",
        git_branch="main",
        git_status=(" M src/example.py",),
        changed_files=("src/example.py",),
    )

    scanner = FakeContextScanner(expected)
    builder = ContextBuilder(scanner)

    context = builder.build()

    assert context == expected


def test_context_builder_scans_exactly_once() -> None:
    expected = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
        git_branch="main",
    )

    scanner = FakeContextScanner(expected)
    builder = ContextBuilder(scanner)

    builder.build()

    assert scanner.calls == 1
