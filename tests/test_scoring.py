from app.analysis.scoring import (
    classify_requirement,
    classify_similarity,
    compute_overall,
    score_clusters,
    similarity_to_percent,
)
from app.analysis.types import AnalysisConfig, ClusterAssignment, RequirementMatch


def _match(
    cluster_id: str,
    similarity: float,
    status: str,
    importance: str = "unspecified",
    evidence_sufficient: bool = True,
) -> RequirementMatch:
    return RequirementMatch(
        requirement_id=f"req_{cluster_id}_{similarity}",
        requirement_text="Need Python experience for backend services.",
        importance=importance,  # type: ignore[arg-type]
        cluster_assignments=(
            ClusterAssignment(
                cluster_id=cluster_id,
                cluster_name=cluster_id.title(),
                relevance=1.0,
            ),
        ),
        evidence_id="ev_0",
        evidence_text="Used Python to build backend services.",
        similarity=similarity,
        evidence_sufficient=evidence_sufficient,
        status=status,  # type: ignore[arg-type]
        explanation="",
    )


def test_classify_similarity_uses_configured_thresholds() -> None:
    assert classify_similarity(0.70, 0.65, 0.40) == "strong"
    assert classify_similarity(0.50, 0.65, 0.40) == "partial"
    assert classify_similarity(0.20, 0.65, 0.40) == "weak"


def test_evidence_sufficiency_gate_overrides_similarity() -> None:
    # Insufficient evidence always yields 'weak' status even if similarity is above threshold
    status = classify_requirement(
        similarity=0.55,
        evidence_sufficient=False,
        strong_threshold=0.65,
        partial_threshold=0.40,
    )
    assert status == "weak"


def test_cluster_score_is_mean_of_requirement_similarities() -> None:
    matches = [_match("programming", 0.80, "strong"), _match("programming", 0.40, "partial")]
    scores = score_clusters(matches, strong_threshold=0.65, partial_threshold=0.40)
    assert len(scores) == 1
    assert scores[0].score == 60.0
    assert scores[0].status == "partial"
    assert scores[0].strong_count == 1
    assert scores[0].partial_count == 1
    assert scores[0].weak_count == 0


def test_importance_does_not_alter_raw_similarity_but_influences_overall() -> None:
    # Required vs Preferred match with same similarity
    match_req = _match("backend", 0.80, "strong", importance="required")
    match_pref = _match("backend", 0.80, "strong", importance="preferred")

    assert match_req.similarity == match_pref.similarity == 0.80

    config = AnalysisConfig()
    breakdown_req = compute_overall([match_req], config)
    breakdown_pref = compute_overall([match_pref], config)

    # Required requirement carries full weight, preferred carries reduced weight
    assert breakdown_req.semantic_alignment == breakdown_pref.semantic_alignment == 80.0


def test_similarity_to_percent_is_clamped() -> None:
    assert similarity_to_percent(1.2) == 100.0
    assert similarity_to_percent(-0.1) == 0.0

