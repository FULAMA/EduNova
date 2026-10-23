from pathlib import Path

from tools.edunova.agents.architect import Architect
from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_analyzer import (
    ContextAnalyzer,
    EngineeringAnalysis,
)
from tools.edunova.agents.inspector import (
    InspectionResult,
    Inspector,
)


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


def inspect(context: EngineeringContext) -> InspectionResult:
    analysis: EngineeringAnalysis = ContextAnalyzer().analyze(context)
    return Inspector().inspect(context, analysis)


def test_architect_preserves_task() -> None:
    context = make_context()
    inspection = inspect(context)

    proposal = Architect().propose(
        task="Ajouter la validation d'une période académique.",
        context=context,
        inspection=inspection,
    )

    assert proposal.task == "Ajouter la validation d'une période académique."


def test_architect_preserves_scope() -> None:
    context = make_context(scope="academic-records")
    inspection = inspect(context)

    proposal = Architect().propose(
        task="Ajouter la validation d'une période académique.",
        context=context,
        inspection=inspection,
    )

    assert proposal.scope == "academic-records"


def test_architect_reports_affected_files() -> None:
    context = make_context(
        changed_files=("src/academic/example.py",),
    )
    inspection = inspect(context)

    proposal = Architect().propose(
        task="Modifier le comportement académique.",
        context=context,
        inspection=inspection,
    )

    assert proposal.affected_files == ("src/academic/example.py",)


def test_architect_preserves_risks() -> None:
    context = make_context(
        risks=("Git status scan failed: fatal error",),
    )
    inspection = inspect(context)

    proposal = Architect().propose(
        task="Analyser le module académique.",
        context=context,
        inspection=inspection,
    )

    assert proposal.risks == ("Git status scan failed: fatal error",)


def test_architect_requires_human_decision_when_risks_exist() -> None:
    context = make_context(
        risks=("Git status scan failed: fatal error",),
    )
    inspection = inspect(context)

    proposal = Architect().propose(
        task="Analyser le module académique.",
        context=context,
        inspection=inspection,
    )

    assert proposal.requires_human_decision is True


def test_architect_requires_no_human_decision_for_clean_context() -> None:
    context = make_context()
    inspection = inspect(context)

    proposal = Architect().propose(
        task="Analyser le module académique.",
        context=context,
        inspection=inspection,
    )

    assert proposal.requires_human_decision is False


def test_architect_is_read_only() -> None:
    context = make_context()
    inspection = inspect(context)

    proposal = Architect().propose(
        task="Analyser le module académique.",
        context=context,
        inspection=inspection,
    )

    assert proposal.read_only is True


def test_architect_rejects_empty_task() -> None:
    context = make_context()
    inspection = inspect(context)

    try:
        Architect().propose(
            task="   ",
            context=context,
            inspection=inspection,
        )
    except ValueError as exc:
        assert "task" in str(exc).lower()
    else:
        raise AssertionError("Expected ValueError")
