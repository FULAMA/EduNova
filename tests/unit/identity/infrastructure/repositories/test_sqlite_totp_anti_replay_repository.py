import tempfile
import threading
from pathlib import Path
from uuid import uuid4


from src.identity.application.interfaces.totp_anti_replay_repository import (
    TotpAntiReplayRepository,
)
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_totp_anti_replay_repository import (
    SQLiteTotpAntiReplayRepository,
)


def get_temp_db() -> SQLiteDatabase:
    temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_file.close()
    db = SQLiteDatabase(Path(temp_file.name))
    db.initialize()
    with db.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS totp_anti_replay (
                user_id TEXT PRIMARY KEY,
                last_accepted_interval INTEGER NOT NULL
            )
        """)
        conn.commit()
    return db


def test_record_interval_first_time_succeeds():
    db = get_temp_db()
    repo: TotpAntiReplayRepository = SQLiteTotpAntiReplayRepository(db)
    user_id = uuid4()
    result = repo.record_interval(user_id=user_id, interval_index=100)
    assert result is True
    assert repo.get_last_interval(user_id) == 100


def test_record_same_interval_fails():
    db = get_temp_db()
    repo: TotpAntiReplayRepository = SQLiteTotpAntiReplayRepository(db)
    user_id = uuid4()
    result1 = repo.record_interval(user_id=user_id, interval_index=100)
    assert result1 is True
    result2 = repo.record_interval(user_id=user_id, interval_index=100)
    assert result2 is False
    assert repo.get_last_interval(user_id) == 100


def test_record_higher_interval_succeeds():
    db = get_temp_db()
    repo: TotpAntiReplayRepository = SQLiteTotpAntiReplayRepository(db)
    user_id = uuid4()
    result1 = repo.record_interval(user_id=user_id, interval_index=100)
    assert result1 is True
    result2 = repo.record_interval(user_id=user_id, interval_index=101)
    assert result2 is True
    assert repo.get_last_interval(user_id) == 101


def test_record_lower_interval_fails():
    db = get_temp_db()
    repo: TotpAntiReplayRepository = SQLiteTotpAntiReplayRepository(db)
    user_id = uuid4()
    result1 = repo.record_interval(user_id=user_id, interval_index=100)
    assert result1 is True
    result2 = repo.record_interval(user_id=user_id, interval_index=99)
    assert result2 is False
    assert repo.get_last_interval(user_id) == 100


def test_get_last_interval_nonexistent_user():
    db = get_temp_db()
    repo: TotpAntiReplayRepository = SQLiteTotpAntiReplayRepository(db)
    user_id = uuid4()
    result = repo.get_last_interval(user_id)
    assert result is None


def test_different_users_are_isolated():
    db = get_temp_db()
    repo: TotpAntiReplayRepository = SQLiteTotpAntiReplayRepository(db)
    user1 = uuid4()
    user2 = uuid4()
    repo.record_interval(user_id=user1, interval_index=100)
    result = repo.record_interval(user_id=user2, interval_index=100)
    assert result is True
    assert repo.get_last_interval(user1) == 100
    assert repo.get_last_interval(user2) == 100


def test_concurrent_same_interval_only_one_succeeds():
    """Requirement 5: Concurrent requests with same interval, only one succeeds."""
    db = get_temp_db()
    user_id = uuid4()
    results = []
    errors = []

    def attempt_record():
        try:
            repo: TotpAntiReplayRepository = SQLiteTotpAntiReplayRepository(db)
            result = repo.record_interval(user_id=user_id, interval_index=200)
            results.append(result)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=attempt_record) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert sum(results) == 1
    assert len(results) == 5
    assert len(errors) == 0


def test_persistence_error_secure_behavior():
    """Requirement 9: Persistence error does not cause insecure 2FA validation."""
    non_existent_db = Path("/tmp/non_existent_" + str(uuid4()) + ".db")
    db = SQLiteDatabase(non_existent_db)
    repo: TotpAntiReplayRepository = SQLiteTotpAntiReplayRepository(db)
    user_id = uuid4()
    result = repo.record_interval(user_id=user_id, interval_index=100)
    assert result is False
