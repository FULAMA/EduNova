from uuid import UUID

from src.academic.application.interfaces.ai_pedagogical_service import AIPedagogicalService
from src.academic.application.interfaces.report_card_repository import ReportCardRepository
from src.academic.application.interfaces.student_repository import StudentRepository
from src.academic.application.interfaces.subject_repository import SubjectRepository


class GenerateReportCardAIFeedback:
    def __init__(
        self,
        ai_service: AIPedagogicalService,
        report_cards: ReportCardRepository,
        students: StudentRepository,
        subjects: SubjectRepository,
    ):
        self._ai = ai_service
        self._report_cards = report_cards
        self._students = students
        self._subjects = subjects

    def execute(self, tenant_id: UUID, report_card_id: UUID) -> dict[str, str]:
        report_card = self._report_cards.find_by_id(report_card_id, tenant_id)
        if report_card is None:
            raise LookupError("Bulletin introuvable dans cet etablissement.")

        student = self._students.get_by_id_and_tenant(report_card.student_id, tenant_id)
        student_name = f"{student.first_name} {student.last_name}" if student else "l'élève"

        snapshot = report_card.snapshot
        general_avg = snapshot.get("general_average", 0.0)
        raw_results = snapshot.get("subject_results", [])
        deliberation = snapshot.get("deliberation", {})
        decision = deliberation.get("decision", "ADMITTED")

        # Résoudre les noms des matières
        subject_ids = {UUID(r["subject_id"]) for r in raw_results if "subject_id" in r}
        subject_map = self._subjects.find_many_by_ids(subject_ids, tenant_id)

        enriched_results = []
        for r in raw_results:
            subj_id = UUID(r["subject_id"]) if "subject_id" in r else None
            subj = subject_map.get(subj_id) if subj_id else None
            enriched_results.append({
                "subject_name": subj.name if subj else "Discipline",
                "average": r.get("average", 0.0),
                "coefficient": r.get("coefficient", 1.0),
            })

        feedback = self._ai.generate_report_card_feedback(
            student_name=student_name,
            general_average=float(general_avg),
            subject_results=enriched_results,
            deliberation_decision=str(decision),
        )

        return {
            "report_card_id": str(report_card_id),
            "student_name": student_name,
            "encouraging": feedback["encouraging"],
            "analytical": feedback["analytical"],
            "demanding": feedback["demanding"],
        }
