from uuid import UUID

from src.academic.application.interfaces.student_repository import StudentRepository
from src.identity.application.interfaces.parent_student_link_repository import (
    ParentStudentLinkRepository,
)
from src.identity.domain.entities.parent_student_link import ParentStudentLink
from src.tenancy.application.interfaces.membership_repository import (
    MembershipRepository,
)


class LinkParentStudent:
    def __init__(
        self,
        link_repository: ParentStudentLinkRepository,
        student_repository: StudentRepository,
        membership_repository: MembershipRepository,
    ):
        self._link_repository = link_repository
        self._student_repository = student_repository
        self._membership_repository = membership_repository

    def execute(
        self,
        tenant_id: UUID,
        parent_user_id: UUID,
        student_id: UUID,
        relationship_type: str,
        actor_id: UUID,
    ) -> ParentStudentLink:
        # 1. Vérifier que l'utilisateur existe dans l'établissement
        membership = self._membership_repository.find_by_user_and_tenant(parent_user_id, tenant_id)
        if (
            membership is None
            or not membership.active
            or membership.role.strip().upper() != "PARENT"
        ):
            raise LookupError("Utilisateur parent introuvable ou inactif dans cet etablissement.")

        # 2. Vérifier que l'élève existe dans l'établissement
        student = self._student_repository.get_by_id_and_tenant(student_id, tenant_id)
        if student is None or not student.active:
            raise LookupError("Eleve introuvable ou inactif dans cet etablissement.")

        # 3. Créer le lien avec validation du type de relation
        link = ParentStudentLink.create(
            tenant_id=tenant_id,
            parent_user_id=parent_user_id,
            student_id=student_id,
            relationship_type=relationship_type,
            created_by=actor_id,
        )
        self._link_repository.save(link)
        return link
