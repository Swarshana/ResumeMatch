# ResumeMatch

Semantic resume-to-job matching with evidence-backed skill gap analysis.

ResumeMatch evaluates how well a resume aligns with a specific job description by identifying the best supporting evidence in the resume for each requirement, rather than relying on simple keyword matching. It provides a detailed, evidence-backed breakdown of strengths and gaps, categorized by skill clusters.

## Why ResumeMatch?

Standard keyword matching often fails to identify semantic equivalents or correctly attribute resume experience to specific job requirements. ResumeMatch addresses this by using semantic embeddings to:
- Tie resume evidence directly back to individual job requirements.
- Filter out unrelated resume text as evidence.
- Aggregate gaps into actionable skill clusters.

## Features

- **Requirement-to-Evidence Matching**: Uses semantic similarity to pair job requirements with the most relevant resume segments.
- **Evidence Sufficiency Gating**: Prevents weak semantic matches from being treated as meaningful evidence.
- **Skill-Cluster Aggregation**: Groups findings into relevant professional domains (e.g., Backend, Frontend, Databases).
- **Evidence-Backed Explanations**: Provides granular, deterministic feedback for each matched requirement.
- **Calibrated Scoring**: Uses tuned thresholds to classify requirements as Strong, Partial, or Weak.
- **Benchmark Evaluation**: Validated against a 35-case labeled dataset for high matching accuracy.

## Architecture

### Backend
- **Framework**: FastAPI
- **Engine**: Framework-agnostic analysis engine using `sentence-transformers/all-MiniLM-L6-v2`.
- **Logic**: Performs preprocessing, requirement-evidence pairing, threshold-based classification, and cluster aggregation.

### Frontend
- **Framework**: Next.js (TypeScript, Tailwind CSS)
- **Role**: Provides a clean, API-driven dashboard to visualize analysis results.

## Matching & Evidence Model

ResumeMatch uses cosine similarity to identify potential evidence for each job requirement.
- **Evidence Threshold (0.35)**: Filters out resume text that is not semantically related to the requirement.
- **Strong Threshold (0.60)**: Indicates the evidence clearly satisfies the requirement.
- **Partial Threshold (0.30)**: Indicates the evidence shows relevant experience but falls short of a full match.

## Evaluation

The engine is calibrated against a 35-case benchmark dataset (v1.0.0).
- **Accuracy**: 82.86%
- **Macro F1**: 0.777

## Running Locally

### Backend
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
Navigate to `frontend/`, create `.env.local` with `NEXT_PUBLIC_API_URL` pointing to your backend, then:
```bash
npm install
npm run build
npm run dev
```

## Testing
```bash
pytest
```

## Limitations
- Performance with highly specialized technical relationships depends on the `MiniLM` model\'s training data.
- Relies on structured text; does not currently perform PDF or DOCX parsing.
- Threshold calibration is based on a focused 35-case benchmark.

## Project Structure
```text
app/                 # FastAPI backend & analysis engine
frontend/            # Next.js dashboard
tests/               # Engine and API tests
```

## Roadmap (NOT IMPLEMENTED)
- PDF/DOCX resume parsing.
- Analysis history / user accounts.
- Downloadable PDF reports.
- Broader industry-specific taxonomies.

