from pathlib import Path

from tools.edunova.agents.architect import (
    ArchitectureProposal,
    Architect,
)
from tools.edunova.agents.context import EngineeringContext
from tools.edunova.agents.context_analyzer import ContextAnalyzer
from tools.edunova.agents.inspector import Inspector
from tools.edunova.agents.reviewer import (
    ReviewStatus,
    Reviewer,
)


def make_proposal(
    *,
    task: str = "Ajouter la validation d'une période académique.",
    risks: tuple[str, ...] = (),
    requires_human_decision: bool = False,
) -> ArchitectureProposal:
    context = EngineeringContext(
        project_root=Path("F:/EduNova"),
        scope="academic-records",
        git_branch="main",
    )

    analysis = ContextAnalyzer().analyze(context)
    inspection = Inspector().inspect(context, analysis)

    return Architect().propose(
        task=task,
        context=context,
        inspection=inspection,
    )


def test_reviewer_approves_clean_proposal() -> None:
    proposal = make_proposal()

    result = Reviewer().review(proposal)

    assert result.status == ReviewStatus.APPROVED


def test_reviewer_preserves_task() -> None:
    proposal = make_proposal()

    result = Reviewer().review(proposal)

    assert result.task == proposal.task


def test_reviewer_blocks_proposal_with_risks() -> None:
    proposal = ArchitectureProposal(
        task="Modifier le module académique.",
        scope="academic-records",
        affected_files=(),
        risks=("Git status scan failed: fatal error",),
        requires_human_decision=False,
        read_only=True,
    )

    result = Reviewer().review(proposal)

    assert result.status == ReviewStatus.BLOCKED


def test_reviewer_requires_human_decision() -> None:
    proposal = ArchitectureProposal(
        task="Modifier le modèle académique.",
        scope="academic-records",
        affected_files=(),
        risks=(),
        requires_human_decision=True,
        read_only=True,
    )

    result = Reviewer().review(proposal)

    assert result.status == ReviewStatus.CHANGES_REQUIRED


def test_reviewer_rejects_non_read_only_proposal() -> None:
    proposal = ArchitectureProposal(
        task="Modifier le modèle académique.",
        scope="academic-records",
        affected_files=(),
        risks=(),
        requires_human_decision=False,
        read_only=False,
    )

    result = Reviewer().review(proposal)

    assert result.status == ReviewStatus.BLOCKED


def test_reviewer_preserves_affected_files() -> None:
    proposal = ArchitectureProposal(
        task="Modifier le modèle académique.",
        scope="academic-records",
        affected_files=("src/academic/example.py",),
        risks=(),
        requires_human_decision=False,
        read_only=True,
    )

    result = Reviewer().review(proposal)

    assert result.affected_files == ("src/academic/example.py",)


def test_reviewer_is_read_only() -> None:
    proposal = make_proposal()

    result = Reviewer().review(proposal)

    assert result.read_only is True


def test_reviewer_rejects_empty_task() -> None:
    proposal = ArchitectureProposal(
        task="   ",
        scope="academic-records",
        affected_files=(),
        risks=(),
        requires_human_decision=False,
        read_only=True,
    )

    result = Reviewer().review(proposal)

    assert result.status == ReviewStatus.BLOCKED
