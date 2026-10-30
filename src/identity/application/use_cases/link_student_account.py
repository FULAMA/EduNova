from datetime import datetime, timezone
from uuid import UUID

from src.academic.application.interfaces.student_repository import StudentRepository
from src.identity.application.interfaces.student_user_link_repository import StudentUserLinkRepository
from src.identity.application.interfaces.user_repository import UserRepository
from src.tenancy.application.interfaces.membership_repository import MembershipRepository
from src.identity.domain.entities.student_user_link import StudentUserLink


class LinkStudentAccount:
    def __init__(
        self,
        links: StudentUserLinkRepository,
        students: StudentRepository,
        users: UserRepository,
        memberships: MembershipRepository,
    ):
        self._links = links
        self._students = students
        self._users = users
        self._memberships = memberships

    def execute(self, tenant_id: UUID, user_id: UUID, student_id: UUID, actor_id: UUID) -> None:
        if self._students.get_by_id_and_tenant(student_id, tenant_id) is None:
            raise ValueError("Eleve introuvable dans cet etablissement.")

        user = self._users.find_by_id(user_id)
        if user is None:
            raise ValueError("Compte utilisateur introuvable.")
        if not user.is_active:
            raise ValueError("Le compte utilisateur est desactive.")

        membership = self._memberships.find_by_user_and_tenant(user_id, tenant_id)
        if membership is None or not membership.active:
            raise ValueError("Le compte ne possede pas de membership actif dans cet etablissement.")
        if membership.role != "STUDENT":
            raise ValueError("Seul un compte ayant le role ELEVE peut etre associe a un eleve.")

        if self._links.find_by_user(user_id, tenant_id):
            raise ValueError("Ce compte est deja associe a un eleve.")

        self._links.save(StudentUserLink(
            tenant_id=tenant_id,
            user_id=user_id,
            student_id=student_id,
            created_by=actor_id,
            created_at=datetime.now(timezone.utc),
        ))
