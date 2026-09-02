from fastapi.testclient import TestClient

from src.presentation.api.app import create_app


class FakeAnalyzeAcademicRisk:

    def execute(self, request):
        return type(
            "FakeResult",
            (),
            {
                "level": "HIGH",
                "score": 90,
                "reasons": (
                    "Moyenne générale particulièrement faible.",
                    "Taux d'assiduité critique.",
                ),
            },
        )()


def test_analyze_academic_risk_route_uses_injected_use_case():
    app = create_app(
        analyze_academic_risk_use_case=FakeAnalyzeAcademicRisk(),
    )

    client = TestClient(app)

    response = client.post(
        "/academic-risk",
        json={
            "average": 7,
            "attendance_rate": 50,
            "unjustified_absences": 6,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["level"] == "HIGH"
    assert body["score"] == 90
    assert len(body["reasons"]) == 2


def test_analyze_academic_risk_rejects_invalid_average():
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/academic-risk",
        json={
            "average": 25,
            "attendance_rate": 80,
            "unjustified_absences": 0,
        },
    )

    assert response.status_code == 422
