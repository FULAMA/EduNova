from types import SimpleNamespace
from uuid import uuid4

from src.academic.domain.entities.student_assignment import StudentAssignmentStatus


def eligible_result_repositories(subject_ids, coefficient=2.0, status=StudentAssignmentStatus.ACTIVE):
    year_id = uuid4()
    class_id = uuid4()
    class_subjects = [
        SimpleNamespace(subject_id=subject_id, active=True, coefficient=coefficient)
        for subject_id in subject_ids
    ]

    class Assignments:
        def list_by_student(self, student_id, tenant_id):
            return [SimpleNamespace(
                student_id=student_id,
                tenant_id=tenant_id,
                academic_year_id=year_id,
                academic_class_id=class_id,
                academic_option_id=None,
                status=status,
            )]

    class Periods:
        def find_by_id(self, period_id, tenant_id):
            return SimpleNamespace(academic_year_id=year_id)

    class ClassSubjects:
        def find_by_class_and_option(self, academic_class_id, academic_option_id, tenant_id):
            return class_subjects

    class Subjects:
        def find_by_id(self, subject_id, tenant_id):
            return SimpleNamespace(id=subject_id, active=True) if any(
                row.subject_id == subject_id for row in class_subjects
            ) else None

    return {
        "assignments": Assignments(),
        "periods": Periods(),
        "class_subjects": ClassSubjects(),
        "subjects": Subjects(),
    }
