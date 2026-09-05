"""Semantic matching helpers: cosine similarity, best evidence, multi-label cluster assignment."""

from __future__ import annotations

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.analysis.types import ClusterAssignment, SkillCluster, TextChunk


def cosine_sim_matrix(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    if left.size == 0 or right.size == 0:
        return np.zeros((left.shape[0], right.shape[0]), dtype=np.float32)
    return cosine_similarity(left, right).astype(np.float32)


def clamp_similarity(score: float) -> float:
    return max(0.0, min(1.0, float(score)))


def best_evidence_matches(
    requirement_embeddings: np.ndarray,
    evidence_embeddings: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """For each requirement, return the index and score of the strongest resume evidence."""
    n_requirements = requirement_embeddings.shape[0]
    if n_requirements == 0:
        return np.array([], dtype=int), np.array([], dtype=np.float32)
    if evidence_embeddings.shape[0] == 0:
        return np.full(n_requirements, -1, dtype=int), np.zeros(n_requirements, dtype=np.float32)

    similarities = cosine_sim_matrix(requirement_embeddings, evidence_embeddings)
    best_indices = similarities.argmax(axis=1)
    best_scores = similarities[np.arange(n_requirements), best_indices]
    return best_indices.astype(int), best_scores.astype(np.float32)


def assign_requirement_clusters(
    requirement_embeddings: np.ndarray,
    cluster_embeddings: np.ndarray,
    clusters: tuple[SkillCluster, ...],
    assignment_threshold: float,
) -> list[list[ClusterAssignment]]:
    """Assign each requirement to every cluster above the threshold, keeping at least the nearest."""
    if requirement_embeddings.shape[0] == 0:
        return []

    similarities = cosine_sim_matrix(requirement_embeddings, cluster_embeddings)
    assignments: list[list[ClusterAssignment]] = []
    for row in similarities:
        selected = [
            ClusterAssignment(
                cluster_id=clusters[index].id,
                cluster_name=clusters[index].name,
                relevance=clamp_similarity(float(score)),
            )
            for index, score in enumerate(row)
            if float(score) >= assignment_threshold
        ]
        if not selected:
            best_index = int(np.argmax(row))
            selected = [
                ClusterAssignment(
                    cluster_id=clusters[best_index].id,
                    cluster_name=clusters[best_index].name,
                    relevance=clamp_similarity(float(row[best_index])),
                )
            ]
        selected.sort(key=lambda item: (-item.relevance, item.cluster_name))
        assignments.append(selected)
    return assignments


def index_chunks(chunks: list[TextChunk] | tuple[TextChunk, ...]) -> dict[str, TextChunk]:
    return {chunk.id: chunk for chunk in chunks}
