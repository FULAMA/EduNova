from src.domain.entities.student_academic_record import StudentAcademicRecord
from src.domain.value_objects.subject_result import SubjectResult


class StudentAcademicRecordMapper:

    @staticmethod
    def to_dict(record: StudentAcademicRecord) -> dict:
        return {
            "student_id": str(record.student_id),
            "academic_period_id": str(record.academic_period_id),
            "subject_results": [
                {
                    "subject_id": str(result.subject_id),
                    "average": result.average,
                    "coefficient": result.coefficient,
                }
                for result in record.subject_results
            ],
            "general_average": record.general_average,
            "failed_subjects": record.failed_subjects,
            "credits_obtained": record.credits_obtained,
            "total_credits": record.total_credits,
        }

    @staticmethod
    def to_domain(data: dict) -> StudentAcademicRecord:
        from uuid import UUID

        subject_results = tuple(
            SubjectResult(
                subject_id=UUID(result["subject_id"]),
                average=result["average"],
                coefficient=result["coefficient"],
            )
            for result in data["subject_results"]
        )

        return StudentAcademicRecord(
            student_id=UUID(data["student_id"]),
            academic_period_id=UUID(data["academic_period_id"]),
            subject_results=subject_results,
            general_average=data["general_average"],
            failed_subjects=data["failed_subjects"],
            credits_obtained=data["credits_obtained"],
            total_credits=data["total_credits"],
        )
