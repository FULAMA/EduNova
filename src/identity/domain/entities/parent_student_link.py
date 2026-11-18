from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from uuid import UUID


class RelationshipType(str, Enum):
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    LEGAL_GUARDIAN = "LEGAL_GUARDIAN"


@dataclass(frozen=True)
class ParentStudentLink:
    tenant_id: UUID
    parent_user_id: UUID
    student_id: UUID
    relationship_type: RelationshipType
    created_by: UUID
    created_at: datetime

    @classmethod
    def create(
        cls,
        tenant_id: UUID,
        parent_user_id: UUID,
        student_id: UUID,
        relationship_type: str,
        created_by: UUID,
    ) -> "ParentStudentLink":
        clean_rel = relationship_type.strip().upper()
        try:
            rel_enum = RelationshipType(clean_rel)
        except ValueError as exc:
            valid_values = ", ".join(r.value for r in RelationshipType)
            raise ValueError(f"Type de lien de parente invalide ({clean_rel}). Autorisés : {valid_values}") from exc

        return cls(
            tenant_id=tenant_id,
            parent_user_id=parent_user_id,
            student_id=student_id,
            relationship_type=rel_enum,
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
        )
