from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gc
from pathlib import Path
import tempfile
from uuid import UUID, uuid4

import pyotp
import pytest

from src.identity.application.dto.verify_login_two_factor_request import (
    VerifyLoginTwoFactorRequest,
)
from src.identity.application.interfaces.totp_anti_replay_repository import (
    TotpAntiReplayRepository,
)
from src.identity.application.interfaces.two_factor_service import TwoFactorService
from src.identity.application.use_cases.verify_login_two_factor import (
    VerifyLoginTwoFactor,
)
from src.identity.domain.entities.user import User
from src.identity.infrastructure.security.in_memory_rate_limiter import (
    InMemoryRateLimiter,
)
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_totp_anti_replay_repository import (
    SQLiteTotpAntiReplayRepository,
)
from src.infrastructure.security.jwt_service import JwtService
from src.tenancy.domain.entities.membership import Membership
from src.tenancy.domain.entities.tenant import Tenant
from tests.support.security import TEST_JWT_SECRET
from tests.support.tenant import TEST_TENANT_ID


class InMemoryUserRepository:
    def __init__(self, users: dict[UUID, User] | None = None):
        self._users = users or {}

    def find_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    def save(self, user: User) -> None:
        self._users[user.id] = user


class InMemoryTenantRepository:
    def __init__(self, tenants: dict[UUID, Tenant] | None = None):
        self._tenants = tenants or {}

    def find_by_id(self, tenant_id: UUID) -> Tenant | None:
        return self._tenants.get(
            tenant_id,
            Tenant(id=tenant_id, name="Test School", slug="test-school", active=True),
        )


class InMemoryMembershipRepository:
    def find_by_user_and_tenant(
        self, user_id: UUID, tenant_id: UUID
    ) -> Membership | None:
        return Membership(
            id=uuid4(),
            user_id=user_id,
            tenant_id=tenant_id,
            role="ADMIN",
            active=True,
        )


class PyOtpTestingTwoFactorService(TwoFactorService):
    def __init__(self, time_provider=None):
        self._time_provider = time_provider or (lambda: datetime.now(timezone.utc).timestamp())

    def generate_secret(self) -> str:
        return pyotp.random_base32()

    def generate_provisioning_uri(self, email: str, secret: str) -> str:
        return pyotp.TOTP(secret).provisioning_uri(name=email, issuer_name="EduNova")

    def verify_code(self, secret: str, code: str) -> bool:
        if not secret or not code or len(code) != 6 or not code.isdigit():
            return False
        dt = datetime.fromtimestamp(self._time_provider(), timezone.utc)
        return pyotp.TOTP(secret).verify(code, for_time=dt)


def create_user(secret: str | None = None) -> tuple[User, str]:
    sec = secret or pyotp.random_base32()
    user = User(
        id=uuid4(),
        email=f"user-{uuid4()}@edunova.com",
        password_hash="argon2-hash",
        role="ADMIN",
        is_active=True,
        two_factor_enabled=True,
        two_factor_secret=sec,
    )
    return user, sec


def create_temp_sqlite_repo() -> tuple[SQLiteDatabase, SQLiteTotpAntiReplayRepository, str]:
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    db_path = temp_file.name

    db = SQLiteDatabase(db_path)
    db.initialize()
    repo = SQLiteTotpAntiReplayRepository(db)
    return db, repo, db_path


# ---------------------------------------------------------------------------
# 1. Premier code TOTP valide accepté
# ---------------------------------------------------------------------------
def test_first_valid_totp_code_accepted():
    db, repo, db_path = create_temp_sqlite_repo()
    try:
        user, secret = create_user()
        user_repo = InMemoryUserRepository({user.id: user})
        jwt_service = JwtService(secret_key=TEST_JWT_SECRET)
        rate_limiter = InMemoryRateLimiter()

        current_time = 1700000000.0  # interval = 1700000000 // 30 = 56666666

        def time_fn():
            return current_time

        use_case = VerifyLoginTwoFactor(
            user_repository=user_repo,
            membership_repository=InMemoryMembershipRepository(),
            tenant_repository=InMemoryTenantRepository(),
            two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
            jwt_service=jwt_service,
            rate_limiter=rate_limiter,
            totp_anti_replay_repository=repo,
            time_provider=time_fn,
        )

        pending_token = jwt_service.create_two_factor_token(
            user_id=user.id, tenant_id=TEST_TENANT_ID
        )
        totp = pyotp.TOTP(secret)
        code = totp.at(int(current_time))

        response = use_case.execute(
            VerifyLoginTwoFactorRequest(
                two_factor_token=pending_token,
                code=code,
            )
        )

        assert response.access_token is not None
        assert response.refresh_token is not None
        assert repo.get_last_interval(user.id) == int(current_time) // 30
    finally:
        del repo
        del db
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 2. Réutilisation du même code rejetée (même session)
# ---------------------------------------------------------------------------
def test_reuse_of_same_code_rejected_same_session():
    db, repo, db_path = create_temp_sqlite_repo()
    try:
        user, secret = create_user()
        user_repo = InMemoryUserRepository({user.id: user})
        jwt_service = JwtService(secret_key=TEST_JWT_SECRET)
        rate_limiter = InMemoryRateLimiter()
        current_time = 1700000000.0

        def time_fn():
            return current_time

        use_case = VerifyLoginTwoFactor(
            user_repository=user_repo,
            membership_repository=InMemoryMembershipRepository(),
            tenant_repository=InMemoryTenantRepository(),
            two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
            jwt_service=jwt_service,
            rate_limiter=rate_limiter,
            totp_anti_replay_repository=repo,
            time_provider=time_fn,
        )

        pending_token = jwt_service.create_two_factor_token(
            user_id=user.id, tenant_id=TEST_TENANT_ID
        )
        code = pyotp.TOTP(secret).at(int(current_time))

        # First verification succeeds
        use_case.execute(
            VerifyLoginTwoFactorRequest(
                two_factor_token=pending_token,
                code=code,
            )
        )

        # Immediate replay with same token is rejected
        with pytest.raises(ValueError, match="Token 2FA deja consomme"):
            use_case.execute(
                VerifyLoginTwoFactorRequest(
                    two_factor_token=pending_token,
                    code=code,
                )
            )
    finally:
        del repo
        del db
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 3. Réutilisation depuis une nouvelle session rejetée (même code, même intervalle)
# ---------------------------------------------------------------------------
def test_reuse_of_same_code_rejected_new_session():
    db, repo, db_path = create_temp_sqlite_repo()
    try:
        user, secret = create_user()
        user_repo = InMemoryUserRepository({user.id: user})
        jwt_service = JwtService(secret_key=TEST_JWT_SECRET)
        rate_limiter = InMemoryRateLimiter()
        current_time = 1700000000.0

        def time_fn():
            return current_time

        use_case = VerifyLoginTwoFactor(
            user_repository=user_repo,
            membership_repository=InMemoryMembershipRepository(),
            tenant_repository=InMemoryTenantRepository(),
            two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
            jwt_service=jwt_service,
            rate_limiter=rate_limiter,
            totp_anti_replay_repository=repo,
            time_provider=time_fn,
        )

        token1 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
        code = pyotp.TOTP(secret).at(int(current_time))

        # Session 1 consumes code
        use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token1, code=code)
        )

        # Attacker/user initiates Session 2 (new pending token) but reuses the same TOTP code
        token2 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)

        with pytest.raises(ValueError, match="Code 2FA deja utilise"):
            use_case.execute(
                VerifyLoginTwoFactorRequest(two_factor_token=token2, code=code)
            )
    finally:
        del repo
        del db
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 4. Réutilisation après redémarrage rejetée
# ---------------------------------------------------------------------------
def test_reuse_after_restart_rejected():
    db1, repo1, db_path = create_temp_sqlite_repo()
    try:
        user, secret = create_user()
        user_repo = InMemoryUserRepository({user.id: user})
        jwt_service = JwtService(secret_key=TEST_JWT_SECRET)
        current_time = 1700000000.0

        def time_fn():
            return current_time

        use_case1 = VerifyLoginTwoFactor(
            user_repository=user_repo,
            membership_repository=InMemoryMembershipRepository(),
            tenant_repository=InMemoryTenantRepository(),
            two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
            jwt_service=jwt_service,
            rate_limiter=InMemoryRateLimiter(),
            totp_anti_replay_repository=repo1,
            time_provider=time_fn,
        )

        token1 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
        code = pyotp.TOTP(secret).at(int(current_time))

        # First session succeeds on process 1
        use_case1.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token1, code=code)
        )

        # Simulate process shutdown: close and delete references
        del use_case1
        del repo1
        del db1
        gc.collect()

        # Process 2 starts up, connects to the same persistent SQLite database
        db2 = SQLiteDatabase(db_path)
        repo2 = SQLiteTotpAntiReplayRepository(db2)

        use_case2 = VerifyLoginTwoFactor(
            user_repository=user_repo,
            membership_repository=InMemoryMembershipRepository(),
            tenant_repository=InMemoryTenantRepository(),
            two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
            jwt_service=jwt_service,
            rate_limiter=InMemoryRateLimiter(),  # completely empty in-memory rate limiter
            totp_anti_replay_repository=repo2,
            time_provider=time_fn,
        )

        token2 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)

        # Must still be rejected because SQLite persisted the interval!
        with pytest.raises(ValueError, match="Code 2FA deja utilise"):
            use_case2.execute(
                VerifyLoginTwoFactorRequest(two_factor_token=token2, code=code)
            )

        del use_case2
        del repo2
        del db2
    finally:
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 5. Deux requêtes concurrentes utilisant le même intervalle : une seule réussit
# ---------------------------------------------------------------------------
def test_concurrent_requests_same_interval_only_one_succeeds():
    db, repo, db_path = create_temp_sqlite_repo()
    try:
        user, secret = create_user()
        user_repo = InMemoryUserRepository({user.id: user})
        jwt_service = JwtService(secret_key=TEST_JWT_SECRET)
        current_time = 1700000000.0

        def time_fn():
            return current_time

        code = pyotp.TOTP(secret).at(int(current_time))
        token1 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
        token2 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)

        use_case = VerifyLoginTwoFactor(
            user_repository=user_repo,
            membership_repository=InMemoryMembershipRepository(),
            tenant_repository=InMemoryTenantRepository(),
            two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
            jwt_service=jwt_service,
            rate_limiter=None,  # Rely exclusively on atomic DB anti-replay
            totp_anti_replay_repository=repo,
            time_provider=time_fn,
        )

        successes = []
        errors = []

        def execute_verification(tok: str):
            try:
                resp = use_case.execute(
                    VerifyLoginTwoFactorRequest(two_factor_token=tok, code=code)
                )
                successes.append(resp)
            except ValueError as e:
                errors.append(str(e))

        with ThreadPoolExecutor(max_workers=2) as executor:
            fut1 = executor.submit(execute_verification, token1)
            fut2 = executor.submit(execute_verification, token2)
            fut1.result()
            fut2.result()

        # Exactly 1 success and 1 rejection
        assert len(successes) == 1
        assert len(errors) == 1
        assert "Code 2FA deja utilise" in errors[0]
    finally:
        del repo
        del db
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 6. Un nouvel intervalle TOTP valide est accepté
# ---------------------------------------------------------------------------
def test_new_valid_totp_interval_accepted():
    db, repo, db_path = create_temp_sqlite_repo()
    try:
        user, secret = create_user()
        user_repo = InMemoryUserRepository({user.id: user})
        jwt_service = JwtService(secret_key=TEST_JWT_SECRET)

        time_state = [1700000000.0]

        def time_fn():
            return time_state[0]

        use_case = VerifyLoginTwoFactor(
            user_repository=user_repo,
            membership_repository=InMemoryMembershipRepository(),
            tenant_repository=InMemoryTenantRepository(),
            two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
            jwt_service=jwt_service,
            rate_limiter=InMemoryRateLimiter(),
            totp_anti_replay_repository=repo,
            time_provider=time_fn,
        )

        totp = pyotp.TOTP(secret)

        # Interval 1: success
        token1 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
        code1 = totp.at(int(time_state[0]))
        resp1 = use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token1, code=code1)
        )
        assert resp1.access_token is not None

        # Advance time by 30 seconds to next interval
        time_state[0] += 30.0

        # Interval 2: success with new token and new code
        token2 = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
        code2 = totp.at(int(time_state[0]))
        resp2 = use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token2, code=code2)
        )
        assert resp2.access_token is not None
        assert repo.get_last_interval(user.id) == int(time_state[0]) // 30
    finally:
        del repo
        del db
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 7. Un code invalide ne consomme pas l'intervalle
# ---------------------------------------------------------------------------
def test_invalid_code_does_not_consume_interval():
    db, repo, db_path = create_temp_sqlite_repo()
    try:
        user, secret = create_user()
        user_repo = InMemoryUserRepository({user.id: user})
        jwt_service = JwtService(secret_key=TEST_JWT_SECRET)
        current_time = 1700000000.0

        def time_fn():
            return current_time

        use_case = VerifyLoginTwoFactor(
            user_repository=user_repo,
            membership_repository=InMemoryMembershipRepository(),
            tenant_repository=InMemoryTenantRepository(),
            two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
            jwt_service=jwt_service,
            rate_limiter=InMemoryRateLimiter(),
            totp_anti_replay_repository=repo,
            time_provider=time_fn,
        )

        token = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)

        # Submit wrong code
        with pytest.raises(ValueError, match="Code 2FA invalide"):
            use_case.execute(
                VerifyLoginTwoFactorRequest(two_factor_token=token, code="000000")
            )

        # Interval was NOT recorded
        assert repo.get_last_interval(user.id) is None

        # User submits correct code for the same interval -> succeeds!
        correct_code = pyotp.TOTP(secret).at(int(current_time))
        resp = use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token, code=correct_code)
        )
        assert resp.access_token is not None
        assert repo.get_last_interval(user.id) == int(current_time) // 30
    finally:
        del repo
        del db
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 8. Un utilisateur différent conserve son propre état anti-rejeu
# ---------------------------------------------------------------------------
def test_different_users_isolated_anti_replay():
    db, repo, db_path = create_temp_sqlite_repo()
    try:
        user1, secret1 = create_user()
        user2, secret2 = create_user()
        user_repo = InMemoryUserRepository({user1.id: user1, user2.id: user2})
        jwt_service = JwtService(secret_key=TEST_JWT_SECRET)
        current_time = 1700000000.0

        def time_fn():
            return current_time

        use_case = VerifyLoginTwoFactor(
            user_repository=user_repo,
            membership_repository=InMemoryMembershipRepository(),
            tenant_repository=InMemoryTenantRepository(),
            two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
            jwt_service=jwt_service,
            rate_limiter=InMemoryRateLimiter(),
            totp_anti_replay_repository=repo,
            time_provider=time_fn,
        )

        token1 = jwt_service.create_two_factor_token(user1.id, TEST_TENANT_ID)
        code1 = pyotp.TOTP(secret1).at(int(current_time))

        token2 = jwt_service.create_two_factor_token(user2.id, TEST_TENANT_ID)
        code2 = pyotp.TOTP(secret2).at(int(current_time))

        # User 1 succeeds
        resp1 = use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token1, code=code1)
        )
        assert resp1.access_token is not None

        # User 2 in the same interval ALSO succeeds (independent state)
        resp2 = use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token2, code=code2)
        )
        assert resp2.access_token is not None

        # User 1 replay attempt is still rejected
        new_token1 = jwt_service.create_two_factor_token(user1.id, TEST_TENANT_ID)
        with pytest.raises(ValueError, match="Code 2FA deja utilise"):
            use_case.execute(
                VerifyLoginTwoFactorRequest(two_factor_token=new_token1, code=code1)
            )
    finally:
        del repo
        del db
        gc.collect()
        try:
            Path(db_path).unlink(missing_ok=True)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# 9. Une erreur de persistance ne provoque pas une validation 2FA non sécurisée
# ---------------------------------------------------------------------------
def test_persistence_error_fails_closed():
    class FailingTotpAntiReplayRepository(TotpAntiReplayRepository):
        def record_interval(self, user_id: UUID, interval_index: int) -> bool:
            # Simulate DB connection failure / error
            return False

        def get_last_interval(self, user_id: UUID) -> int | None:
            return None

    user, secret = create_user()
    user_repo = InMemoryUserRepository({user.id: user})
    jwt_service = JwtService(secret_key=TEST_JWT_SECRET)
    current_time = 1700000000.0
    def time_fn():
        return current_time

    use_case = VerifyLoginTwoFactor(
        user_repository=user_repo,
        membership_repository=InMemoryMembershipRepository(),
        tenant_repository=InMemoryTenantRepository(),
        two_factor_service=PyOtpTestingTwoFactorService(time_provider=time_fn),
        jwt_service=jwt_service,
        rate_limiter=InMemoryRateLimiter(),
        totp_anti_replay_repository=FailingTotpAntiReplayRepository(),
        time_provider=time_fn,
    )

    token = jwt_service.create_two_factor_token(user.id, TEST_TENANT_ID)
    code = pyotp.TOTP(secret).at(int(current_time))

    with pytest.raises(ValueError, match="Code 2FA deja utilise"):
        use_case.execute(
            VerifyLoginTwoFactorRequest(two_factor_token=token, code=code)
        )
