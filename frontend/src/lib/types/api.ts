export type MatchStatus = 'strong' | 'partial' | 'weak';

export interface EvidenceItem {
  id: string;
  text: string;
}

export interface RequirementMatch {
  id: string;
  text: string;
  cluster_id: string;
  cluster_name: string;
  best_evidence_id: string | null;
  best_evidence_text: string | null;
  similarity: number;
  similarity_percent: number;
  status: MatchStatus;
  explanation: string;
}

export interface ClusterResult {
  id: string;
  name: string;
  score: number;
  status: MatchStatus;
  requirement_count: number;
  matched_requirements: RequirementMatch[];
  weak_requirements: RequirementMatch[];
}

export interface AnalyzeResponse {
  overall_score: number;
  overall_status: MatchStatus;
  summary: string;
  skill_clusters: ClusterResult[];
  matched_requirements: RequirementMatch[];
  weak_requirements: RequirementMatch[];
  resume_evidence: EvidenceItem[];
  job_requirements: EvidenceItem[];
  explanations: string[];
}
