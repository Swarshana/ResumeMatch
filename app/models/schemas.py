"""API request/response schemas for the future Next.js client."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

MatchStatus = Literal["strong", "partial", "weak"]


class AnalyzeRequest(BaseModel):
    resume: str = Field(min_length=1, description="Plain-text resume")
    job_description: str = Field(min_length=1, description="Plain-text job description")

    def __init__(self, **data):
        super().__init__(**data)
        if not self.resume.strip():
            raise ValueError("Resume cannot be whitespace-only.")
        if not self.job_description.strip():
            raise ValueError("Job description cannot be whitespace-only.")


class EvidenceItem(BaseModel):
    id: str
    text: str


class RequirementMatchModel(BaseModel):
    id: str
    text: str
    cluster_id: str
    cluster_name: str
    best_evidence_id: str | None
    best_evidence_text: str | None
    similarity: float = Field(ge=0.0, le=1.0)
    similarity_percent: float = Field(ge=0.0, le=100.0)
    status: MatchStatus
    explanation: str


class ClusterResultModel(BaseModel):
    id: str
    name: str
    score: float = Field(ge=0.0, le=100.0)
    status: MatchStatus
    requirement_count: int
    matched_requirements: list[RequirementMatchModel]
    weak_requirements: list[RequirementMatchModel]


class AnalyzeResponse(BaseModel):
    overall_score: float = Field(ge=0.0, le=100.0)
    overall_status: MatchStatus
    summary: str
    skill_clusters: list[ClusterResultModel]
    matched_requirements: list[RequirementMatchModel]
    weak_requirements: list[RequirementMatchModel]
    resume_evidence: list[EvidenceItem]
    job_requirements: list[EvidenceItem]
    explanations: list[str]
