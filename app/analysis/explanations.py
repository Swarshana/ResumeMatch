"""Deterministic, evidence-backed explanations. No LLM in V1."""

from __future__ import annotations

from app.analysis.types import ClusterScore, MatchStatus, RequirementMatch


def explain_requirement(match: RequirementMatch) -> str:
    requirement = _quote(match.requirement_text)
    cluster = match.primary_cluster.cluster_name if match.cluster_assignments else "General"
    percent = round(match.similarity * 100.0, 1)

    if match.evidence_text is None or not match.evidence_sufficient:
        if match.evidence_text is not None:
            evidence = _quote(match.evidence_text)
            return (
                f"The job requires {requirement}. "
                f"The closest resume evidence is {evidence} "
                f"(similarity {percent}%). This is a weak/missing match in {cluster} "
                f"because the resume does not sufficiently support this requirement."
            )
        return (
            f"The job requires {requirement} under {cluster}. "
            f"No usable resume evidence was found, so this is a weak gap."
        )

    evidence = _quote(match.evidence_text)
    if match.status == "strong":
        return (
            f"The job requires {requirement}. "
            f"The resume supports this with {evidence} "
            f"(similarity {percent}%). This is a strong match in {cluster}."
        )
    if match.status == "partial":
        return (
            f"The job requires {requirement}. "
            f"The closest resume evidence is {evidence} "
            f"(similarity {percent}%). This is only a partial match in {cluster} "
            f"because the evidence is related but does not fully cover the requirement."
        )
    return (
        f"The job requires {requirement}. "
        f"The closest resume evidence is {evidence} "
        f"(similarity {percent}%). This is a weak/missing match in {cluster} "
        f"because the resume does not sufficiently support this requirement."
    )


def summarize(
    overall_percent: float,
    overall_status: MatchStatus,
    cluster_scores: list[ClusterScore] | tuple[ClusterScore, ...],
    matches: list[RequirementMatch] | tuple[RequirementMatch, ...],
) -> str:
    strong_clusters = [item.cluster_name for item in cluster_scores if item.status == "strong"]
    partial_clusters = [item.cluster_name for item in cluster_scores if item.status == "partial"]
    weak_clusters = [item.cluster_name for item in cluster_scores if item.status == "weak"]
    weak_count = sum(1 for item in matches if item.status == "weak")

    parts = [
        f"Overall semantic alignment is {overall_percent:.1f}% ({overall_status})."
    ]
    if strong_clusters:
        parts.append(f"Strong clusters: {_join_names(strong_clusters)}.")
    if partial_clusters:
        parts.append(f"Partial clusters: {_join_names(partial_clusters)}.")
    if weak_clusters:
        parts.append(f"Weak or missing clusters: {_join_names(weak_clusters)}.")
    if weak_count:
        parts.append(f"{weak_count} job requirement(s) lack sufficient resume evidence.")
    elif matches:
        parts.append("Every extracted job requirement has at least partial resume support.")
    return " ".join(parts)


def _quote(text: str, limit: int = 180) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) > limit:
        cleaned = cleaned[: limit - 1].rstrip() + "…"
    return f'"{cleaned}"'


def _join_names(names: list[str]) -> str:
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{', '.join(names[:-1])}, and {names[-1]}"
