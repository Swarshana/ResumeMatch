"""Resume-to-job analysis pipeline. Independent of FastAPI."""

from __future__ import annotations

from dataclasses import replace

from app.analysis.embeddings import Embedder
from app.analysis.explanations import explain_requirement, summarize
from app.analysis.importance import detect_importance
from app.analysis.matching import assign_requirement_clusters, best_evidence_matches
from app.analysis.preprocessing import to_text_chunks
from app.analysis.scoring import (
    classify_requirement,
    compute_overall,
    overall_status_from_score,
    score_clusters,
)
from app.analysis.taxonomy import Taxonomy
from app.analysis.types import (
    AnalysisConfig,
    AnalysisResult,
    ClusterAssignment,
    RequirementMatch,
)


class AnalysisPipeline:
    def __init__(
        self,
        embedder: Embedder,
        taxonomy: Taxonomy,
        config: AnalysisConfig | None = None,
        strong_threshold: float = 0.65,
        partial_threshold: float = 0.40,
        min_chunk_chars: int = 20,
        max_chunk_chars: int = 420,
    ) -> None:
        self._embedder = embedder
        self._taxonomy = taxonomy
        if config is not None:
            self._config = config
        else:
            self._config = AnalysisConfig(
                strong_threshold=strong_threshold,
                partial_threshold=partial_threshold,
                min_chunk_chars=min_chunk_chars,
                max_chunk_chars=max_chunk_chars,
            )
        self._cluster_embeddings = self._embedder.embed(self._taxonomy.embedding_texts())

    def analyze(self, resume: str, job_description: str) -> AnalysisResult:
        resume_chunks = to_text_chunks(
            resume,
            source="resume",
            min_chars=self._config.min_chunk_chars,
            max_chars=self._config.max_chunk_chars,
        )
        job_chunks = to_text_chunks(
            job_description,
            source="job",
            min_chars=self._config.min_chunk_chars,
            max_chars=self._config.max_chunk_chars,
        )

        cluster_embeddings = self._cluster_embeddings
        requirement_embeddings = self._embedder.embed([chunk.text for chunk in job_chunks])
        evidence_embeddings = self._embedder.embed([chunk.text for chunk in resume_chunks])

        evidence_indices, similarities = best_evidence_matches(
            requirement_embeddings,
            evidence_embeddings,
        )
        cluster_assignments = assign_requirement_clusters(
            requirement_embeddings,
            cluster_embeddings,
            self._taxonomy.clusters,
            self._config.cluster_assignment_threshold,
        )

        matches: list[RequirementMatch] = []
        fallback_cluster = (
            ClusterAssignment(
                cluster_id=self._taxonomy.clusters[0].id,
                cluster_name=self._taxonomy.clusters[0].name,
                relevance=1.0,
            ),
        )

        for index, requirement in enumerate(job_chunks):
            similarity = float(similarities[index]) if index < len(similarities) else 0.0
            evidence_index = int(evidence_indices[index]) if index < len(evidence_indices) else -1
            evidence = (
                resume_chunks[evidence_index]
                if 0 <= evidence_index < len(resume_chunks)
                else None
            )
            evidence_sufficient = (
                evidence is not None and similarity >= self._config.evidence_threshold
            )
            importance = detect_importance(requirement.text, section=requirement.section)
            assignments = (
                tuple(cluster_assignments[index])
                if index < len(cluster_assignments) and cluster_assignments[index]
                else fallback_cluster
            )
            status = classify_requirement(
                similarity,
                evidence_sufficient,
                self._config.strong_threshold,
                self._config.partial_threshold,
            )
            draft = RequirementMatch(
                requirement_id=requirement.id,
                requirement_text=requirement.text,
                importance=importance,
                cluster_assignments=assignments,
                evidence_id=evidence.id if evidence else None,
                evidence_text=evidence.text if evidence else None,
                similarity=similarity,
                evidence_sufficient=evidence_sufficient,
                status=status,
                explanation="",
            )
            matches.append(replace(draft, explanation=explain_requirement(draft)))

        cluster_scores = score_clusters(
            matches,
            self._config.strong_threshold,
            self._config.partial_threshold,
        )
        breakdown = compute_overall(matches, self._config)
        overall = breakdown.overall_score
        status = overall_status_from_score(
            overall,
            self._config.strong_threshold,
            self._config.partial_threshold,
        )
        summary = summarize(overall, status, cluster_scores, matches)
        return AnalysisResult(
            overall_score=overall,
            overall_status=status,
            score_breakdown=breakdown,
            summary=summary,
            resume_chunks=tuple(resume_chunks),
            job_chunks=tuple(job_chunks),
            requirement_matches=tuple(matches),
            cluster_scores=tuple(cluster_scores),
            explanations=tuple(item.explanation for item in matches),
        )
