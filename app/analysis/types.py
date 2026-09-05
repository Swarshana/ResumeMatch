"""Domain types for the analysis engine. These stay independent of FastAPI."""

from dataclasses import dataclass, field
from typing import Literal

MatchStatus = Literal["strong", "partial", "weak"]
RequirementImportance = Literal["required", "preferred", "unspecified"]


@dataclass(frozen=True)
class AnalysisConfig:
    """Calibration knobs for matching and scoring. Not scientific constants."""

    strong_threshold: float = 0.65
    partial_threshold: float = 0.40
    evidence_threshold: float = 0.35
    cluster_assignment_threshold: float = 0.40
    alignment_weight: float = 0.65
    coverage_weight: float = 0.35
    gap_penalty: float = 0.45
    preferred_weight: float = 0.50
    min_chunk_chars: int = 20
    max_chunk_chars: int = 420


@dataclass(frozen=True)
class TextChunk:
    id: str
    text: str
    source: Literal["resume", "job"]
    section: str | None = None


@dataclass(frozen=True)
class SkillCluster:
    id: str
    name: str
    description: str
    examples: tuple[str, ...]

    def embedding_text(self) -> str:
        examples = ", ".join(self.examples)
        return f"{self.name}. {self.description} Skills include: {examples}."


@dataclass(frozen=True)
class ClusterAssignment:
    """How relevant a requirement is to a skill cluster. Independent of resume match."""

    cluster_id: str
    cluster_name: str
    relevance: float


@dataclass(frozen=True)
class RequirementMatch:
    requirement_id: str
    requirement_text: str
    importance: RequirementImportance
    cluster_assignments: tuple[ClusterAssignment, ...]
    evidence_id: str | None
    evidence_text: str | None
    similarity: float
    evidence_sufficient: bool
    status: MatchStatus
    explanation: str

    @property
    def primary_cluster(self) -> ClusterAssignment:
        return self.cluster_assignments[0]


@dataclass(frozen=True)
class ClusterScore:
    cluster_id: str
    cluster_name: str
    score: float
    status: MatchStatus
    mean_relevance: float
    requirement_ids: tuple[str, ...]
    required_count: int = 0
    preferred_count: int = 0
    strong_count: int = 0
    partial_count: int = 0
    weak_count: int = 0


@dataclass(frozen=True)
class ScoreBreakdown:
    """Explainable overall-score components. Not a hiring or interview probability."""

    semantic_alignment: float
    requirement_coverage: float
    weak_penalty: float
    overall_score: float


@dataclass(frozen=True)
class AnalysisResult:
    overall_score: float
    overall_status: MatchStatus
    score_breakdown: ScoreBreakdown
    summary: str
    resume_chunks: tuple[TextChunk, ...]
    job_chunks: tuple[TextChunk, ...]
    requirement_matches: tuple[RequirementMatch, ...]
    cluster_scores: tuple[ClusterScore, ...]
    explanations: tuple[str, ...] = field(default_factory=tuple)
