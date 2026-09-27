import pytest
from fastapi.testclient import TestClient

from src.infrastructure.persistence.database import SQLiteDatabase
from src.presentation.api.container import ApplicationContainer
from src.presentation.api.app import create_app

@pytest.fixture(scope="session")
def template_database():
    db = SQLiteDatabase(":memory:")
    db.initialize()
    yield db
    if db._connection:
        db._connection.close()

@pytest.fixture(scope="function")
def memory_database(template_database):
    new_db = SQLiteDatabase(":memory:")
    new_conn = new_db.connect()
    template_conn = template_database.connect()
    template_conn.backup(new_conn)

    new_db.initialize = lambda: None

    yield new_db

    if new_db._connection:
        new_db._connection.close()

@pytest.fixture(scope="function")
def application_container(memory_database):
    return ApplicationContainer(database=memory_database)

@pytest.fixture(scope="function")
def api_client(application_container):
    app = create_app(container=application_container)
    return TestClient(app)
