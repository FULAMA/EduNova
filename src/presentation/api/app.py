from fastapi import FastAPI

from src.presentation.api.routes.academic_records import router as academic_records_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="EduNova API",
        description="API REST du systeme academique EduNova",
        version="1.0.0",
    )

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {
            "status": "ok",
            "application": "EduNova",
        }

    app.include_router(academic_records_router)

    return app


app = create_app()
