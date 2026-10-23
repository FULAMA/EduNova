from pathlib import Path

from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_analyzer import ContextAnalyzer


def test_analyzer_reports_scope() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="academic-records",
        git_branch="main",
    )

    analysis = ContextAnalyzer().analyze(context)

    assert analysis.scope == "academic-records"


def test_analyzer_reports_changed_files() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="academic-records",
        git_branch="main",
        git_status=(" M src/example.py", "?? tests/example.py"),
        changed_files=("src/example.py", "tests/example.py"),
    )

    analysis = ContextAnalyzer().analyze(context)

    assert analysis.changed_files == (
        "src/example.py",
        "tests/example.py",
    )
    assert analysis.changed_file_count == 2


def test_analyzer_reports_architecture() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
        architecture=(
            "src/academic",
            "src/identity",
            "src/tenancy",
            "tools/edunova/agents",
        ),
    )

    analysis = ContextAnalyzer().analyze(context)

    assert analysis.architecture == (
        "src/academic",
        "src/identity",
        "src/tenancy",
        "tools/edunova/agents",
    )


def test_analyzer_reports_tests() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
        tests=(
            "tests/unit",
            "tests/integration",
        ),
    )

    analysis = ContextAnalyzer().analyze(context)

    assert analysis.tests == (
        "tests/unit",
        "tests/integration",
    )


def test_analyzer_reports_decisions() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
        decisions=(
            "tenant_id is mandatory",
            "human approval is required for sensitive decisions",
        ),
    )

    analysis = ContextAnalyzer().analyze(context)

    assert analysis.decisions == (
        "tenant_id is mandatory",
        "human approval is required for sensitive decisions",
    )


def test_analyzer_reports_git_risks() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
        git_branch="",
        risks=("Git branch scan failed: fatal error",),
    )

    analysis = ContextAnalyzer().analyze(context)

    assert analysis.risks == ("Git branch scan failed: fatal error",)


def test_analyzer_marks_clean_context() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
        git_branch="main",
    )

    analysis = ContextAnalyzer().analyze(context)

    assert analysis.is_clean is True


def test_analyzer_marks_context_with_changes_as_not_clean() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
        git_branch="main",
        git_status=(" M src/example.py",),
        changed_files=("src/example.py",),
    )

    analysis = ContextAnalyzer().analyze(context)

    assert analysis.is_clean is False


def test_analyzer_preserves_branch() -> None:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="agent-kernel",
        git_branch="feature/context-analysis",
    )

    analysis = ContextAnalyzer().analyze(context)

    assert analysis.git_branch == "feature/context-analysis"
