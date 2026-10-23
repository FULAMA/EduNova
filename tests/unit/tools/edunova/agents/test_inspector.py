from pathlib import Path

from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_analyzer import (
    ContextAnalyzer,
    EngineeringAnalysis,
)
from tools.edunova.agents.inspector import Inspector


def make_context(
    *,
    scope: str = "academic-records",
    changed_files: tuple[str, ...] = (),
    risks: tuple[str, ...] = (),
) -> EngineeringContext:
    return EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope=scope,
        git_branch="main",
        changed_files=changed_files,
        risks=risks,
    )


def analyze(context: EngineeringContext) -> EngineeringAnalysis:
    return ContextAnalyzer().analyze(context)


def test_inspector_preserves_scope() -> None:
    context = make_context()

    result = Inspector().inspect(
        context,
        analyze(context),
    )

    assert result.scope == "academic-records"


def test_inspector_reports_changed_file_count() -> None:
    context = make_context(
        changed_files=(
            "src/academic/example.py",
            "tests/academic/example.py",
        ),
    )

    result = Inspector().inspect(
        context,
        analyze(context),
    )

    assert result.changed_file_count == 2


def test_inspector_reports_risks() -> None:
    context = make_context(
        risks=("Git status scan failed: fatal error",),
    )

    result = Inspector().inspect(
        context,
        analyze(context),
    )

    assert result.risks == ("Git status scan failed: fatal error",)


def test_inspector_requests_human_review_when_risks_exist() -> None:
    context = make_context(
        risks=("Git status scan failed: fatal error",),
    )

    result = Inspector().inspect(
        context,
        analyze(context),
    )

    assert result.requires_human_review is True


def test_inspector_does_not_request_review_for_clean_context() -> None:
    context = make_context()

    result = Inspector().inspect(
        context,
        analyze(context),
    )

    assert result.requires_human_review is False


def test_inspector_identifies_affected_files() -> None:
    context = make_context(
        changed_files=("src/example.py",),
    )

    result = Inspector().inspect(
        context,
        analyze(context),
    )

    assert result.affected_files == ("src/example.py",)


def test_inspector_is_read_only() -> None:
    context = make_context()

    result = Inspector().inspect(
        context,
        analyze(context),
    )

    assert result.read_only is True
