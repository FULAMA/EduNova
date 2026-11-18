from src.integrations.application.interfaces.notification_service import NotificationService
from uuid import uuid4

from src.identity.application.dto.register_establishment_request import (
    RegisterEstablishmentRequest,
)
from src.identity.application.dto.register_establishment_response import (
    RegisterEstablishmentResponse,
)
from src.identity.application.interfaces.password_hasher import PasswordHasher
from src.identity.application.interfaces.user_repository import UserRepository
from src.identity.domain.entities.user import User
from src.tenancy.application.interfaces.establishment_provisioning_unit_of_work import (
    EstablishmentProvisioningConflict,
    EstablishmentProvisioningFailure,
    EstablishmentProvisioningUnitOfWork,
)
from src.tenancy.application.interfaces.tenant_repository import TenantRepository
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant
from src.tenancy.domain.services.tenant_slug_service import TenantSlugService


class RegisterEstablishment:
    """Use case to autonomously provision a new educational establishment.

    Orchestrates the atomic creation of:
    1. A Tenant representing the school, with a guaranteed unique slug.
    2. A User account for the school administrator, securely hashed with Argon2id.
    3. An authoritative Membership granting the ADMIN role to this user for this tenant.

    All technical identifiers and privileges are assigned strictly server-side.
    Persistence is wrapped in a single database transaction, ensuring no partial
    or orphaned entities remain on failure.
    """

    def __init__(
        self,
        unit_of_work: EstablishmentProvisioningUnitOfWork,
        tenant_repository: TenantRepository,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        slug_service: TenantSlugService | None = None,
        notification_service: NotificationService | None = None,
    ):
        self._unit_of_work = unit_of_work
        self._tenant_repository = tenant_repository
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._slug_service = slug_service or TenantSlugService()
        self._notification_service = notification_service

    def execute(
        self,
        request: RegisterEstablishmentRequest,
    ) -> RegisterEstablishmentResponse:
        school_name = request.school_name.strip() if request.school_name else ""
        admin_name = request.admin_name.strip() if request.admin_name else ""
        raw_email = request.email.strip() if request.email else ""
        password = request.password

        # 1. Input validations
        if not school_name:
            raise ValueError("Le nom de l etablissement ne peut pas etre vide.")

        if not admin_name:
            raise ValueError("Le nom complet du responsable ne peut pas etre vide.")

        if not raw_email:
            raise ValueError("L email ne peut pas etre vide.")

        if "@" not in raw_email or len(raw_email) < 5 or "." not in raw_email.split("@")[-1]:
            raise ValueError("Format d email invalide.")

        if not password:
            raise ValueError("Le mot de passe ne peut pas etre vide.")

        if len(password) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caracteres.")

        # 2. Email normalization
        normalized_email = raw_email.lower()

        # 3. Identity availability check
        existing_user = self._user_repository.find_by_email(normalized_email)
        if existing_user is not None:
            raise ValueError("Cette adresse email est deja utilisee.")

        # 4. Technical ID generation (server-side only)
        tenant_id = uuid4()
        user_id = uuid4()
        membership_id = uuid4()

        # 5. Guaranteed unique slug generation
        slug = self._slug_service.generate_unique_slug(
            school_name,
            is_slug_taken=lambda s: self._tenant_repository.find_by_slug(s) is not None,
        )

        # 6. Secure password hashing
        password_hash = self._password_hasher.hash(password)

        # 7. Domain entity construction
        tenant = Tenant(
            id=tenant_id,
            name=school_name,
            slug=slug,
            active=True,
        )
        user = User(
            id=user_id,
            email=normalized_email,
            password_hash=password_hash,
            role="ADMIN",
            is_active=True,
        )
        membership = Membership(
            id=membership_id,
            user_id=user_id,
            tenant_id=tenant_id,
            role="ADMIN",
            active=True,
        )

        # 8. Atomic persistence in a single transaction
        try:
            self._unit_of_work.provision_establishment_atomic(
                tenant=tenant,
                user=user,
                membership=membership,
            )
        except EstablishmentProvisioningConflict as exc:
            if exc.resource == "email":
                raise ValueError("Cette adresse email est deja utilisee.") from None
            if exc.resource == "slug":
                # Concurrent race condition on slug: retry with short random hex suffix
                new_slug = f"{slug[:40]}-{uuid4().hex[:6]}"
                retry_tenant = Tenant(
                    id=tenant_id,
                    name=school_name,
                    slug=new_slug,
                    active=True,
                )
                try:
                    self._unit_of_work.provision_establishment_atomic(
                        tenant=retry_tenant,
                        user=user,
                        membership=membership,
                    )
                    tenant = retry_tenant
                except (EstablishmentProvisioningConflict, EstablishmentProvisioningFailure):
                    raise ValueError(
                        "Impossible de reserver cet identifiant d etablissement. Veuillez reessayer."
                    ) from None
            else:
                # Sanitized message, never expose raw SQL syntax or DB schema
                raise ValueError(
                    "Une erreur d integrite est survenue lors de la creation de l etablissement."
                ) from None
        except EstablishmentProvisioningFailure:
            raise ValueError(
                "Une erreur est survenue lors de la creation de l etablissement."
            ) from None

        # Trigger welcome notification (INT-007: failsafe, does not block registration)
        if self._notification_service is not None:
            try:
                self._notification_service.send_email(
                    to_email=user.email,
                    subject=f"Bienvenue sur EduNova - {tenant.name}",
                    body=(
                        f"Bonjour {admin_name},\n\n"
                        f"Votre etablissement {tenant.name} a ete cree avec succes sur EduNova.\n"
                        f"Identifiant de l'etablissement: {tenant.id}\n"
                        f"Identifiant d'acces (slug): {tenant.slug}\n\n"
                        f"Cordialement,\nL'equipe EduNova"
                    ),
                )
            except Exception:
                pass

        # 9. Return safe response without credentials or internal secrets
        return RegisterEstablishmentResponse(
            tenant_id=tenant.id,
            tenant_name=tenant.name,
            tenant_slug=tenant.slug,
            user_id=user.id,
            admin_name=admin_name,
            email=user.email,
            role=membership.role,
        )
