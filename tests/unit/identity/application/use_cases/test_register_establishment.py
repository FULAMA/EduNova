from uuid import UUID, uuid4

import pytest

from src.identity.application.dto.register_establishment_request import (
    RegisterEstablishmentRequest,
)
from src.identity.application.dto.register_establishment_response import (
    RegisterEstablishmentResponse,
)
from src.identity.application.interfaces.password_hasher import PasswordHasher
from src.identity.application.use_cases.register_establishment import (
    RegisterEstablishment,
)
from src.identity.domain.entities.user import User
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_user_repository import (
    SQLiteUserRepository,
)
from src.tenancy.domain.entities.tenant import Tenant
from src.tenancy.infrastructure.persistence.sqlite_establishment_provisioning_uow import (
    SQLiteEstablishmentProvisioningUnitOfWork,
)
from src.tenancy.infrastructure.repositories.sqlite_membership_repository import (
    SQLiteMembershipRepository,
)
from src.tenancy.infrastructure.repositories.sqlite_tenant_repository import (
    SQLiteTenantRepository,
)


class DummyPasswordHasher(PasswordHasher):
    """Predictable Argon2id-style test hasher for isolated unit testing."""

    def hash(self, password: str) -> str:
        if not password:
            raise ValueError("Le mot de passe ne peut pas etre vide.")
        return f"$argon2id$v=19$m=65536,t=3,p=4$fake_salt${password}_hashed"

    def verify(self, password: str, password_hash: str) -> bool:
        expected = f"$argon2id$v=19$m=65536,t=3,p=4$fake_salt${password}_hashed"
        return password_hash == expected


def setup_test_environment(tmp_path):
    db_path = str(tmp_path / "test_reg_establishment.db")
    database = SQLiteDatabase(db_path)
    with database.connect() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                active INTEGER NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                is_active INTEGER NOT NULL,
                two_factor_enabled INTEGER NOT NULL,
                two_factor_secret TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memberships (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                role TEXT NOT NULL,
                active INTEGER NOT NULL,
                UNIQUE (user_id, tenant_id),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (tenant_id) REFERENCES tenants (id) ON DELETE CASCADE
            )
            """
        )

    tenant_repo = SQLiteTenantRepository(database)
    user_repo = SQLiteUserRepository(database)
    membership_repo = SQLiteMembershipRepository(database)
    uow = SQLiteEstablishmentProvisioningUnitOfWork(
        database=database,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        membership_repository=membership_repo,
    )
    hasher = DummyPasswordHasher()
    use_case = RegisterEstablishment(
        unit_of_work=uow,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        password_hasher=hasher,
    )

    return database, tenant_repo, user_repo, membership_repo, hasher, use_case


# 1. Nominal establishment registration
def test_register_establishment_nominal(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, use_case = setup_test_environment(tmp_path)

    request = RegisterEstablishmentRequest(
        school_name="Complexe Scolaire Boboto",
        admin_name="Jean-Pierre Malula",
        email="direction@cs-boboto.cd",
        password="SecurePassword2026!",
    )

    response = use_case.execute(request)

    assert isinstance(response, RegisterEstablishmentResponse)
    assert isinstance(response.tenant_id, UUID)
    assert isinstance(response.user_id, UUID)
    assert response.tenant_name == "Complexe Scolaire Boboto"
    assert response.tenant_slug == "complexe-scolaire-boboto"
    assert response.admin_name == "Jean-Pierre Malula"
    assert response.email == "direction@cs-boboto.cd"
    assert response.role == "ADMIN"

    # Verify persisted in database
    saved_tenant = tenant_repo.find_by_id(response.tenant_id)
    assert saved_tenant is not None
    assert saved_tenant.active is True

    saved_user = user_repo.find_by_id(response.user_id)
    assert saved_user is not None
    assert saved_user.is_active is True


# 2. First administrator creation with ADMIN role
def test_register_establishment_creates_first_admin(tmp_path):
    _, _, user_repo, membership_repo, _, use_case = setup_test_environment(tmp_path)

    request = RegisterEstablishmentRequest(
        school_name="Lycée Motema Mpiko",
        admin_name="Soeur Marie",
        email="direction@motemampiko.cd",
        password="StrongPassword2026!",
    )

    response = use_case.execute(request)

    # Authority comes from Membership
    membership = membership_repo.find_by_user_and_tenant(response.user_id, response.tenant_id)
    assert membership is not None
    assert membership.role == "ADMIN"
    assert membership.active is True


# 3. Correct User-Tenant-Membership linkage
def test_register_establishment_user_tenant_membership_linkage(tmp_path):
    _, tenant_repo, user_repo, membership_repo, _, use_case = setup_test_environment(tmp_path)

    request = RegisterEstablishmentRequest(
        school_name="Institut Kimwenza",
        admin_name="Professeur Mwamba",
        email="mwamba@kimwenza.cd",
        password="SuperSecretPassword1!",
    )

    response = use_case.execute(request)

    membership = membership_repo.find_by_user_and_tenant(response.user_id, response.tenant_id)
    assert membership is not None
    assert membership.user_id == response.user_id
    assert membership.tenant_id == response.tenant_id


# 4. Password securely hashed
def test_register_establishment_password_securely_hashed(tmp_path):
    _, _, user_repo, _, hasher, use_case = setup_test_environment(tmp_path)

    raw_password = "MyComplexPassword2026@"
    request = RegisterEstablishmentRequest(
        school_name="Collège Saint Raphaël",
        admin_name="Abbé François",
        email="direction@st-raphael.cd",
        password=raw_password,
    )

    response = use_case.execute(request)

    user = user_repo.find_by_id(response.user_id)
    assert user is not None
    assert user.password_hash != raw_password
    assert hasher.verify(raw_password, user.password_hash) is True
    assert hasher.verify("WrongPassword", user.password_hash) is False


# 5. Rejection of already used email
def test_register_establishment_rejects_already_used_email(tmp_path):
    _, tenant_repo, user_repo, _, hasher, use_case = setup_test_environment(tmp_path)

    # Pre-seed an existing user
    user_repo.save(
        User(
            id=uuid4(),
            email="already_used@edunova.cd",
            password_hash=hasher.hash("SomePassword123!"),
            role="ADMIN",
        )
    )

    # Attempt to register with the exact email (even with different casing)
    request = RegisterEstablishmentRequest(
        school_name="Nouvelle École",
        admin_name="Jacques Kabeya",
        email="  ALREADY_USED@edunova.cd  ",
        password="NewPassword1234!",
    )

    with pytest.raises(ValueError, match="Cette adresse email est deja utilisee."):
        use_case.execute(request)

    # Verify no tenant was created
    assert tenant_repo.find_by_slug("nouvelle-ecole") is None


# 6. Slug uniqueness and collision handling
def test_register_establishment_slug_uniqueness(tmp_path):
    _, tenant_repo, _, _, _, use_case = setup_test_environment(tmp_path)

    # Register school 1
    req1 = RegisterEstablishmentRequest(
        school_name="Institut Lumumba",
        admin_name="Directeur Un",
        email="admin1@lumumba.cd",
        password="Password1234!",
    )
    resp1 = use_case.execute(req1)
    assert resp1.tenant_slug == "institut-lumumba"

    # Register school 2 with the exact same name
    req2 = RegisterEstablishmentRequest(
        school_name="Institut Lumumba",
        admin_name="Directeur Deux",
        email="admin2@lumumba.cd",
        password="Password1234!",
    )
    resp2 = use_case.execute(req2)
    assert resp2.tenant_slug == "institut-lumumba-2"
    assert resp2.tenant_id != resp1.tenant_id


# 7. Concurrent slug collision handling at persistence level
def test_register_establishment_concurrent_slug_collision_handled(tmp_path):
    database, tenant_repo, user_repo, membership_repo, hasher, _ = setup_test_environment(tmp_path)

    class CollidingSlugService:
        def generate_unique_slug(self, name, is_slug_taken):
            # Forces returning an existing slug to simulate race condition between check and insert
            return "collision-slug"

    # Pre-seed tenant with "collision-slug"
    tenant_repo.save(Tenant(id=uuid4(), name="Existing", slug="collision-slug", active=True))

    use_case_with_collision = RegisterEstablishment(
        unit_of_work=SQLiteEstablishmentProvisioningUnitOfWork(
            database=database,
            tenant_repository=tenant_repo,
            user_repository=user_repo,
            membership_repository=membership_repo,
        ),
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        password_hasher=hasher,
        slug_service=CollidingSlugService(),  # type: ignore[arg-type]
    )

    req = RegisterEstablishmentRequest(
        school_name="École Test",
        admin_name="Responsable",
        email="admin@test-concurrent.cd",
        password="Password1234!",
    )

    response = use_case_with_collision.execute(req)
    # The use case retried with a unique hex suffix
    assert response.tenant_slug.startswith("collision-slug-")
    assert tenant_repo.find_by_slug(response.tenant_slug) is not None


# 8. Complete transactional rollback on failure
def test_register_establishment_complete_rollback_on_failure(tmp_path):
    _, tenant_repo, user_repo, membership_repo, hasher, _ = setup_test_environment(tmp_path)

    class FailingUnitOfWork:
        def provision_establishment_atomic(self, tenant, user, membership):
            raise RuntimeError("Database connection suddenly dropped!")

    failing_use_case = RegisterEstablishment(
        unit_of_work=FailingUnitOfWork(),  # type: ignore[arg-type]
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        password_hasher=hasher,
    )

    req = RegisterEstablishmentRequest(
        school_name="École Échouée",
        admin_name="Jean Échec",
        email="echec@edunova.cd",
        password="Password1234!",
    )

    with pytest.raises(RuntimeError, match="Database connection suddenly dropped!"):
        failing_use_case.execute(req)

    # Verify zero partial entities remain in repositories
    assert tenant_repo.find_by_slug("ecole-echouee") is None
    assert user_repo.find_by_email("echec@edunova.cd") is None


# 9. Response contains no sensitive data
def test_register_establishment_response_no_sensitive_data(tmp_path):
    _, _, _, _, _, use_case = setup_test_environment(tmp_path)

    req = RegisterEstablishmentRequest(
        school_name="Institut de la Gombe",
        admin_name="Madame Directrice",
        email="direction@gombe.cd",
        password="TopSecretPassword123!",
    )

    resp = use_case.execute(req)

    response_dict = resp.__dict__
    assert "password" not in response_dict
    assert "password_hash" not in response_dict
    assert "two_factor_secret" not in response_dict
    assert "salt" not in response_dict


# 10. Client cannot supply tenant_id or role
def test_register_establishment_client_cannot_control_privileges():
    # Attempting to supply unwanted arguments raises TypeError
    with pytest.raises(TypeError):
        RegisterEstablishmentRequest(  # type: ignore[call-arg]
            school_name="École Hacker",
            admin_name="Hacker",
            email="hacker@edunova.cd",
            password="Password123!",
            role="SUPERADMIN",
            tenant_id=uuid4(),
        )


# 11. Input validations
@pytest.mark.parametrize(
    "school_name,admin_name,email,password,expected_error",
    [
        ("", "Admin", "a@b.cd", "password123", "Le nom de l etablissement ne peut pas etre vide."),
        ("  ", "Admin", "a@b.cd", "password123", "Le nom de l etablissement ne peut pas etre vide."),
        ("École", "", "a@b.cd", "password123", "Le nom complet du responsable ne peut pas etre vide."),
        ("École", "Admin", "", "password123", "L email ne peut pas etre vide."),
        ("École", "Admin", "invalid-email", "password123", "Format d email invalide."),
        ("École", "Admin", "a@b", "password123", "Format d email invalide."),
        ("École", "Admin", "a@b.cd", "", "Le mot de passe ne peut pas etre vide."),
        ("École", "Admin", "a@b.cd", "short", "Le mot de passe doit contenir au moins 8 caracteres."),
    ],
)
def test_register_establishment_validations(tmp_path, school_name, admin_name, email, password, expected_error):
    _, _, _, _, _, use_case = setup_test_environment(tmp_path)

    req = RegisterEstablishmentRequest(
        school_name=school_name,
        admin_name=admin_name,
        email=email,
        password=password,
    )

    with pytest.raises(ValueError, match=expected_error):
        use_case.execute(req)


def test_register_establishment_sends_welcome_notification(tmp_path):
    class MockNotificationService:
        def __init__(self):
            self.emails_sent = []

        def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False, **kwargs):
            self.emails_sent.append({"to": to_email, "subject": subject, "body": body})
            return True

    mock_notifier = MockNotificationService()
    database, tenant_repo, user_repo, membership_repo, hasher, _ = setup_test_environment(tmp_path)
    uow = SQLiteEstablishmentProvisioningUnitOfWork(
        database=database,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        membership_repository=membership_repo,
    )
    use_case = RegisterEstablishment(
        unit_of_work=uow,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        password_hasher=hasher,
        notification_service=mock_notifier,
    )

    req = RegisterEstablishmentRequest(
        school_name="Collège Saint Joseph",
        admin_name="Père Recteur",
        email="recteur@stjoseph.cd",
        password="ValidPassword123!",
    )
    res = use_case.execute(req)
    assert res.email == "recteur@stjoseph.cd"
    assert len(mock_notifier.emails_sent) == 1
    assert mock_notifier.emails_sent[0]["to"] == "recteur@stjoseph.cd"
    assert "Bienvenue sur EduNova" in mock_notifier.emails_sent[0]["subject"]


def test_register_establishment_notification_failure_does_not_block(tmp_path):
    class BrokenNotificationService:
        def send_email(self, *args, **kwargs):
            raise RuntimeError("SMTP connection timeout")

    database, tenant_repo, user_repo, membership_repo, hasher, _ = setup_test_environment(tmp_path)
    uow = SQLiteEstablishmentProvisioningUnitOfWork(
        database=database,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        membership_repository=membership_repo,
    )
    use_case = RegisterEstablishment(
        unit_of_work=uow,
        tenant_repository=tenant_repo,
        user_repository=user_repo,
        password_hasher=hasher,
        notification_service=BrokenNotificationService(),
    )

    req = RegisterEstablishmentRequest(
        school_name="Lycée Shaumba",
        admin_name="Sœur Directrice",
        email="directrice@shaumba.cd",
        password="ValidPassword123!",
    )
    res = use_case.execute(req)
    assert res.tenant_slug == "lycee-shaumba"
