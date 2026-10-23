from src.presentation.api.app import create_app


def test_factory_uses_database_path_from_environment(
    monkeypatch,
    tmp_path,
):
    database_path = tmp_path / "factory.db"
    monkeypatch.setenv("EDUNOVA_ENVIRONMENT", "test")
    monkeypatch.setenv("EDUNOVA_DATABASE_PATH", str(database_path))
    monkeypatch.setenv(
        "EDUNOVA_JWT_SECRET",
        "factory-test-secret-1234567890",
    )

    create_app()

    assert database_path.exists()
