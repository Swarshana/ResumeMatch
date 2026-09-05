from fastapi.testclient import TestClient

from app.analysis.pipeline import AnalysisPipeline
from app.api.routes import get_pipeline
from app.main import create_app


def test_analyze_endpoint_returns_structured_payload(pipeline: AnalysisPipeline) -> None:
    application = create_app(warmup_embedder=False)
    application.dependency_overrides[get_pipeline] = lambda: pipeline
    client = TestClient(application)

    response = client.post(
        "/api/analyze",
        json={
            "resume": (
                "Built REST APIs with FastAPI and PostgreSQL. "
                "Wrote unit tests with pytest for backend services."
            ),
            "job_description": (
                "Experience building REST APIs with FastAPI and PostgreSQL. "
                "Production Kubernetes experience required."
            ),
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "overall_score" in payload
    assert "skill_clusters" in payload
    assert "explanations" in payload
    assert payload["job_requirements"]
    assert payload["summary"]


def test_analyze_rejects_empty_input(pipeline: AnalysisPipeline) -> None:
    application = create_app(warmup_embedder=False)
    application.dependency_overrides[get_pipeline] = lambda: pipeline
    client = TestClient(application)
    
    # Test whitespace only
    response = client.post("/api/analyze", json={"resume": "   ", "job_description": "   "})
    assert response.status_code == 422

    # Test missing fields
    response = client.post("/api/analyze", json={})
    assert response.status_code == 422


def test_health() -> None:
    client = TestClient(create_app(warmup_embedder=False))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
