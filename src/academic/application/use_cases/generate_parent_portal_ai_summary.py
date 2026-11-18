from typing import Any
from uuid import UUID

from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository
from src.academic.application.interfaces.ai_pedagogical_service import AIPedagogicalService
from src.academic.application.interfaces.report_card_repository import ReportCardRepository
from src.academic.application.interfaces.student_repository import StudentRepository
from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.domain.entities.report_card import ReportCardStatus
from src.identity.application.interfaces.parent_student_link_repository import (
    ParentStudentLinkRepository,
)


class GenerateParentPortalAISummary:
    def __init__(
        self,
        ai_service: AIPedagogicalService,
        parent_student_links: ParentStudentLinkRepository,
        report_cards: ReportCardRepository,
        students: StudentRepository,
        periods: AcademicPeriodRepository,
        subjects: SubjectRepository,
    ):
        self._ai = ai_service
        self._links = parent_student_links
        self._report_cards = report_cards
        self._students = students
        self._periods = periods
        self._subjects = subjects

    def execute(
        self,
        tenant_id: UUID,
        parent_user_id: UUID,
        student_id: UUID,
        report_card_id: UUID,
    ) -> dict[str, Any]:
        # Règle impérative PAR-REL-06 : contrôle strict du rattachement officiel parent-élève
        if not self._links.is_parent_of(tenant_id, parent_user_id, student_id):
            raise PermissionError("Accès refusé : vous n'êtes pas officiellement associé à cet élève.")

        report_card = self._report_cards.find_by_id(report_card_id, tenant_id)
        if report_card is None or report_card.student_id != student_id:
            raise LookupError("Bulletin introuvable pour cet élève dans cet établissement.")

        if report_card.status is not ReportCardStatus.ISSUED:
            raise ValueError("Le résumé IA n'est disponible que pour les bulletins officiellement publiés.")

        student = self._students.get_by_id_and_tenant(student_id, tenant_id)
        student_name = f"{student.first_name} {student.last_name}" if student else "votre enfant"

        period = self._periods.find_by_id(report_card.academic_period_id, tenant_id)
        period_name = period.name if period else "Trimestre"

        snapshot = report_card.snapshot
        general_avg = float(snapshot.get("general_average", 0.0))
        deliberation = snapshot.get("deliberation", {})
        decision = str(deliberation.get("decision", "ADMIS"))

        raw_results = snapshot.get("subject_results", [])
        subject_ids = {UUID(r["subject_id"]) for r in raw_results if "subject_id" in r}
        subject_map = self._subjects.find_many_by_ids(subject_ids, tenant_id)

        strong_points: list[str] = []
        focus_areas: list[str] = []
        for r in raw_results:
            subj_id = UUID(r["subject_id"]) if "subject_id" in r else None
            subj_name = subject_map[subj_id].name if subj_id and subj_id in subject_map else "Matière"
            avg = r.get("average", 0.0)
            if avg >= 13:
                strong_points.append(subj_name)
            elif avg < 10:
                focus_areas.append(subj_name)

        attendance_summary = "L'assiduité en classe est satisfaisante"

        summary = self._ai.generate_parent_summary(
            student_name=student_name,
            period_name=period_name,
            general_average=general_avg,
            deliberation_decision=decision,
            strong_points=strong_points,
            focus_areas=focus_areas,
            attendance_summary=attendance_summary,
        )

        return {
            "student_id": str(student_id),
            "report_card_id": str(report_card_id),
            "period_name": period_name,
            "headline": summary["headline"],
            "summary": summary["summary"],
            "tips_for_home": summary["tips_for_home"],
        }
