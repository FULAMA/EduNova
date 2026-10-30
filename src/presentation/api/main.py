import os

from src.presentation.api.app import create_app

app = create_app(
    database_path=os.getenv("EDUNOVA_DATABASE_PATH", "edunova.db"),
)
