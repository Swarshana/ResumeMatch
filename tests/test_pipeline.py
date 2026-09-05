from app.analysis.pipeline import AnalysisPipeline
from app.analysis.taxonomy import load_taxonomy


def test_pipeline_identifies_strong_and_weak_clusters(pipeline: AnalysisPipeline) -> None:
    resume = """
    - Built REST APIs with FastAPI and PostgreSQL for internal developer tools.
    - Wrote unit tests with pytest for backend services and API contracts.
    """
    job = """
    - Experience building REST APIs with FastAPI and PostgreSQL.
    - Production Kubernetes and AWS deployment experience.
    """
    result = pipeline.analyze(resume, job)
    assert result.job_chunks
    assert result.resume_chunks
    assert 0 <= result.overall_score <= 100
    assert result.requirement_matches

    by_text = {item.requirement_text: item for item in result.requirement_matches}
    fastapi_match = next(item for item in result.requirement_matches if "FastAPI" in item.requirement_text)
    kubernetes_match = next(item for item in result.requirement_matches if "Kubernetes" in item.requirement_text)
    assert fastapi_match.similarity > kubernetes_match.similarity
    assert kubernetes_match.status in {"partial", "weak"}
    assert fastapi_match.evidence_text is not None
    assert "FastAPI" in fastapi_match.explanation
    clusters = {item.cluster_id for item in result.cluster_scores}
    assert clusters <= {cluster.id for cluster in load_taxonomy().clusters}
    assert by_text  # sanity: mapping built


def test_pipeline_handles_empty_resume(pipeline: AnalysisPipeline) -> None:
    job = "- Experience building REST APIs with FastAPI and PostgreSQL for production systems."
    result = pipeline.analyze(" ", job)
    assert result.resume_chunks == ()
    assert all(item.status == "weak" for item in result.requirement_matches)
    assert all(item.evidence_id is None for item in result.requirement_matches)
