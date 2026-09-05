import numpy as np

from app.analysis.matching import assign_requirement_clusters, best_evidence_matches, cosine_sim_matrix
from app.analysis.taxonomy import load_taxonomy
from app.analysis.types import SkillCluster


def test_best_evidence_picks_highest_cosine() -> None:
    requirements = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    evidence = np.array([[0.9, 0.1], [0.1, 0.9]], dtype=np.float32)
    indices, scores = best_evidence_matches(requirements, evidence)
    assert list(indices) == [0, 1]
    assert scores[0] > 0.9
    assert scores[1] > 0.9


def test_empty_evidence_yields_zero_scores() -> None:
    requirements = np.array([[1.0, 0.0]], dtype=np.float32)
    evidence = np.zeros((0, 2), dtype=np.float32)
    indices, scores = best_evidence_matches(requirements, evidence)
    assert list(indices) == [-1]
    assert list(scores) == [0.0]


def test_assign_clusters_uses_nearest_description() -> None:
    clusters = (
        SkillCluster("a", "A", "alpha", ()),
        SkillCluster("b", "B", "beta", ()),
    )
    requirement_embeddings = np.array([[0.0, 1.0]], dtype=np.float32)
    cluster_embeddings = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    assigned = assign_requirement_clusters(requirement_embeddings, cluster_embeddings, clusters, assignment_threshold=0.40)
    assert assigned[0][0].cluster_id == "b"


def test_cosine_handles_empty_inputs() -> None:
    left = np.zeros((0, 3), dtype=np.float32)
    right = np.zeros((2, 3), dtype=np.float32)
    matrix = cosine_sim_matrix(left, right)
    assert matrix.shape == (0, 2)


def test_multi_label_cluster_assignment_preserves_scores_and_primary() -> None:
    clusters = (
        SkillCluster("backend", "Backend Development", "desc", ()),
        SkillCluster("cloud", "Cloud & DevOps", "desc", ()),
        SkillCluster("frontend", "Frontend Development", "desc", ()),
    )
    # Unit-normalized requirement vector with strong backend and cloud components
    vec = np.array([0.9, 0.75, 0.1], dtype=np.float32)
    norm = np.linalg.norm(vec)
    req_emb = np.array([vec / norm], dtype=np.float32)
    c_emb = np.eye(3, dtype=np.float32)

    # Threshold chosen so backend (0.9/norm ~ 0.765) and cloud (0.75/norm ~ 0.638) qualify
    assignments = assign_requirement_clusters(req_emb, c_emb, clusters, assignment_threshold=0.60)
    assert len(assignments) == 1
    req_assignments = assignments[0]

    assert len(req_assignments) == 2
    assert req_assignments[0].cluster_id == "backend"
    assert req_assignments[0].relevance > 0.70
    assert req_assignments[1].cluster_id == "cloud"
    assert req_assignments[1].relevance > 0.60


def test_no_assigned_cluster_above_threshold_falls_back_safely() -> None:
    clusters = (
        SkillCluster("a", "A", "desc", ()),
        SkillCluster("b", "B", "desc", ()),
    )
    vec = np.array([0.2, 0.3], dtype=np.float32)
    norm = np.linalg.norm(vec)
    req_emb = np.array([vec / norm], dtype=np.float32)
    c_emb = np.eye(2, dtype=np.float32)

    # Cosine similarities: b is 0.3/norm ~ 0.832, a is 0.2/norm ~ 0.555
    # High threshold 0.90 -> none meet threshold
    assignments = assign_requirement_clusters(req_emb, c_emb, clusters, assignment_threshold=0.90)
    assert len(assignments) == 1
    assert len(assignments[0]) == 1
    assert assignments[0][0].cluster_id == "b"
    assert assignments[0][0].relevance > 0.80


def test_multi_label_edge_cases_with_taxonomy() -> None:
    taxonomy = load_taxonomy()
    cluster_names = [c.name for c in taxonomy.clusters]
    assert "Backend Development" in cluster_names
    assert "Programming" in cluster_names
    assert "Frontend Development" in cluster_names
    assert "System Design" in cluster_names
    assert "Machine Learning" in cluster_names
    assert "Cloud & DevOps" in cluster_names
