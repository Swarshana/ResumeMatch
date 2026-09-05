"""Maps analysis-engine results into API response models."""

from __future__ import annotations

from app.analysis.scoring import similarity_to_percent
from app.analysis.types import AnalysisResult, RequirementMatch
from app.models.schemas import (
    AnalyzeResponse,
    ClusterResultModel,
    EvidenceItem,
    RequirementMatchModel,
)


def to_response(result: AnalysisResult) -> AnalyzeResponse:
    match_models = [_requirement_model(item) for item in result.requirement_matches]
    by_id = {item.id: item for item in match_models}

    clusters = []
    for cluster in result.cluster_scores:
        cluster_matches = [by_id[requirement_id] for requirement_id in cluster.requirement_ids]
        clusters.append(
            ClusterResultModel(
                id=cluster.cluster_id,
                name=cluster.cluster_name,
                score=cluster.score,
                status=cluster.status,
                requirement_count=len(cluster_matches),
                matched_requirements=[item for item in cluster_matches if item.status != "weak"],
                weak_requirements=[item for item in cluster_matches if item.status == "weak"],
            )
        )

    return AnalyzeResponse(
        overall_score=result.overall_score,
        overall_status=result.overall_status,
        summary=result.summary,
        skill_clusters=clusters,
        matched_requirements=[item for item in match_models if item.status != "weak"],
        weak_requirements=[item for item in match_models if item.status == "weak"],
        resume_evidence=[EvidenceItem(id=chunk.id, text=chunk.text) for chunk in result.resume_chunks],
        job_requirements=[EvidenceItem(id=chunk.id, text=chunk.text) for chunk in result.job_chunks],
        explanations=list(result.explanations),
    )


def _requirement_model(match: RequirementMatch) -> RequirementMatchModel:
    primary = match.primary_cluster
    return RequirementMatchModel(
        id=match.requirement_id,
        text=match.requirement_text,
        cluster_id=primary.cluster_id,
        cluster_name=primary.cluster_name,
        best_evidence_id=match.evidence_id,
        best_evidence_text=match.evidence_text,
        similarity=round(match.similarity, 4),
        similarity_percent=similarity_to_percent(match.similarity),
        status=match.status,
        explanation=match.explanation,
    )
