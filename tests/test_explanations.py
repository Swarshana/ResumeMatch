from app.analysis.explanations import explain_requirement, summarize
from app.analysis.types import ClusterAssignment, ClusterScore, RequirementMatch


def test_strong_explanation_includes_requirement_and_evidence() -> None:
    match = RequirementMatch(
        requirement_id="req_0",
        requirement_text="Experience with sentence embeddings and semantic similarity.",
        importance="unspecified",
        cluster_assignments=(
            ClusterAssignment("ai_nlp", "AI / NLP", 1.0),
        ),
        evidence_id="ev_0",
        evidence_text="Built a semantic similarity pipeline using sentence embeddings.",
        similarity=0.82,
        evidence_sufficient=True,
        status="strong",
        explanation="",
    )
    text = explain_requirement(match)
    assert "sentence embeddings" in text
    assert "semantic similarity pipeline" in text
    assert "strong match" in text
    assert "AI / NLP" in text
    assert "82.0%" in text


def test_weak_explanation_is_not_generic_advice() -> None:
    match = RequirementMatch(
        requirement_id="req_1",
        requirement_text="Production Kubernetes experience.",
        importance="unspecified",
        cluster_assignments=(
            ClusterAssignment("cloud_devops", "Cloud & DevOps", 1.0),
        ),
        evidence_id="ev_1",
        evidence_text="Completed an introductory HTML workshop.",
        similarity=0.12,
        evidence_sufficient=False,
        status="weak",
        explanation="",
    )
    text = explain_requirement(match)
    assert "You should improve" not in text
    assert "Production Kubernetes experience" in text
    assert "introductory HTML workshop" in text
    assert "weak/missing" in text


def test_summary_lists_cluster_statuses() -> None:
    summary = summarize(
        overall_percent=71.5,
        overall_status="strong",
        cluster_scores=[
            ClusterScore("backend", "Backend Development", 80.0, "strong", 100.0, ("req_0",)),
            ClusterScore("testing", "Testing", 22.0, "weak", 100.0, ("req_1",)),
        ],
        matches=[
            RequirementMatch("req_0", "a", "unspecified", (ClusterAssignment("backend", "Backend Development", 1.0),), "ev_0", "b", 0.8, True, "strong", ""),
            RequirementMatch("req_1", "c", "unspecified", (ClusterAssignment("testing", "Testing", 1.0),), "ev_1", "d", 0.2, False, "weak", ""),
        ],
    )
    assert "71.5%" in summary
    assert "Backend Development" in summary
    assert "Testing" in summary
    assert "1 job requirement" in summary
