"""Cluster-level and overall scoring. Thresholds come from configuration.

Overall score formula (not a hiring or interview probability):

    w_i = 1.0 for required/unspecified requirements, else preferred_weight

    semantic_alignment = Σ(similarity_i * w_i) / Σ w_i
    requirement_coverage = Σ(w_i for non-weak i) / Σ w_i
    weak_ratio = 1 - requirement_coverage

    alignment_weight' and coverage_weight' are normalized to sum to 1
    combined = alignment_weight' * semantic_alignment
               + coverage_weight' * requirement_coverage
    weak_penalty = gap_penalty * weak_ratio
    overall = max(0, combined - weak_penalty)

Cluster score formula:

    For requirements assigned to cluster C,
    score_C = Σ(similarity_i * relevance_i,C) / Σ relevance_i,C

    Relevance is cluster membership strength, not resume match. A requirement
    that is only weakly about C influences C less than one that is clearly about C.
    The same requirement may inform multiple clusters without being added into
    the overall score more than once (overall is requirement-based, not a sum
    of cluster scores).
"""

from __future__ import annotations

from collections import defaultdict

from app.analysis.matching import clamp_similarity
from app.analysis.types import (
    AnalysisConfig,
    ClusterScore,
    MatchStatus,
    RequirementImportance,
    RequirementMatch,
    ScoreBreakdown,
)


def classify_similarity(score: float, strong_threshold: float, partial_threshold: float) -> MatchStatus:
    if score >= strong_threshold:
        return "strong"
    if score >= partial_threshold:
        return "partial"
    return "weak"


def classify_requirement(
    similarity: float,
    evidence_sufficient: bool,
    strong_threshold: float,
    partial_threshold: float,
) -> MatchStatus:
    if not evidence_sufficient:
        return "weak"
    return classify_similarity(similarity, strong_threshold, partial_threshold)


def similarity_to_percent(score: float) -> float:
    return round(max(0.0, min(1.0, float(score))) * 100.0, 1)


def importance_weight(importance: RequirementImportance, preferred_weight: float) -> float:
    if importance == "preferred":
        return preferred_weight
    return 1.0


def score_clusters(
    matches: list[RequirementMatch] | tuple[RequirementMatch, ...],
    strong_threshold: float,
    partial_threshold: float,
) -> list[ClusterScore]:
    grouped: dict[tuple[str, str], list[tuple[RequirementMatch, float]]] = defaultdict(list)
    for match in matches:
        for assignment in match.cluster_assignments:
            grouped[(assignment.cluster_id, assignment.cluster_name)].append(
                (match, assignment.relevance)
            )

    scores: list[ClusterScore] = []
    for (cluster_id, cluster_name), items in grouped.items():
        weight_sum = sum(relevance for _, relevance in items)
        if weight_sum <= 0:
            weighted_match = sum(item.similarity for item, _ in items) / len(items)
            mean_relevance = 0.0
        else:
            weighted_match = sum(item.similarity * relevance for item, relevance in items) / weight_sum
            mean_relevance = weight_sum / len(items)
        required_cnt = sum(1 for item, _ in items if item.importance in ("required", "unspecified"))
        preferred_cnt = sum(1 for item, _ in items if item.importance == "preferred")
        strong_cnt = sum(1 for item, _ in items if item.status == "strong")
        partial_cnt = sum(1 for item, _ in items if item.status == "partial")
        weak_cnt = sum(1 for item, _ in items if item.status == "weak")

        scores.append(
            ClusterScore(
                cluster_id=cluster_id,
                cluster_name=cluster_name,
                score=similarity_to_percent(weighted_match),
                status=classify_similarity(weighted_match, strong_threshold, partial_threshold),
                mean_relevance=similarity_to_percent(mean_relevance),
                requirement_ids=tuple(item.requirement_id for item, _ in items),
                required_count=required_cnt,
                preferred_count=preferred_cnt,
                strong_count=strong_cnt,
                partial_count=partial_cnt,
                weak_count=weak_cnt,
            )
        )
    scores.sort(key=lambda item: (-item.score, item.cluster_name))
    return scores


def compute_overall(matches: list[RequirementMatch] | tuple[RequirementMatch, ...], config: AnalysisConfig) -> ScoreBreakdown:
    if not matches:
        return ScoreBreakdown(
            semantic_alignment=0.0,
            requirement_coverage=0.0,
            weak_penalty=0.0,
            overall_score=0.0,
        )

    weights = [importance_weight(item.importance, config.preferred_weight) for item in matches]
    weight_sum = sum(weights) or 1.0
    alignment = sum(item.similarity * weight for item, weight in zip(matches, weights)) / weight_sum
    coverage = (
        sum(weight for item, weight in zip(matches, weights) if item.status != "weak") / weight_sum
    )
    weak_ratio = 1.0 - coverage

    raw_align = config.alignment_weight
    raw_cover = config.coverage_weight
    mix_total = raw_align + raw_cover
    if mix_total <= 0:
        align_w, cover_w = 1.0, 0.0
    else:
        align_w, cover_w = raw_align / mix_total, raw_cover / mix_total

    combined = align_w * alignment + cover_w * coverage
    penalty = config.gap_penalty * weak_ratio
    overall = max(0.0, combined - penalty)

    return ScoreBreakdown(
        semantic_alignment=similarity_to_percent(alignment),
        requirement_coverage=similarity_to_percent(coverage),
        weak_penalty=similarity_to_percent(penalty),
        overall_score=similarity_to_percent(overall),
    )


def overall_status_from_score(percent: float, strong_threshold: float, partial_threshold: float) -> MatchStatus:
    return classify_similarity(percent / 100.0, strong_threshold, partial_threshold)


def clamp_match_similarity(score: float) -> float:
    return clamp_similarity(score)
