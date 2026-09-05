# ResumeMatch

**Semantic resume-to-job matching with evidence-backed skill gap analysis.**

ResumeMatch evaluates how well a resume aligns with a specific job description by identifying the best supporting evidence in the resume for each requirement, rather than relying on simple keyword matching. It produces requirement-level classifications, evidence-backed explanations, and actionable skill-cluster insights.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)
![Next.js](https://img.shields.io/badge/Next.js-Dashboard-black)
![Tests](https://img.shields.io/badge/Tests-42_passed-success)

## V1 Results (Benchmark v1.0.0)

| Metric | Result |
|---|---:|
| Benchmark Accuracy | **82.86%** |
| Macro F1 | **0.777** |
| Benchmark Cases | 35 |
| Tests Passing | **42/42** |

*Calibration improved benchmark accuracy from 71.43% to 82.86%.*

## Why ResumeMatch?

Standard keyword matching often fails to identify semantic equivalents or correctly attribute resume experience to specific job requirements. ResumeMatch addresses this by using semantic embeddings to ensure that experience is not just detected, but correctly tied to individual job requirements.

## Features

- **Semantic Matching**: Pairs job requirements with the most relevant resume segments.
- **Evidence Gating**: Filters out weak semantic matches.
- **Skill-Cluster Aggregation**: Groups results by professional domain.
- **Evidence-Backed Explanations**: Provides granular, deterministic feedback.
- **Calibrated Scoring**: Classifies requirements as Strong, Partial, or Weak.
- **Benchmark Evaluation**: Validated against 35 labeled cases.
- **API-Driven**: FastAPI backend with a Next.js dashboard.

## Pipeline Architecture

```text
Job Description ? Requirement Extraction
        ?
Semantic Embedding (all-MiniLM-L6-v2)
        ?
Resume Evidence Matching
        ?
Evidence Sufficiency Gate
        ?
Strong / Partial / Weak Classification
        ?
Importance-Aware Scoring
        ?
Skill Cluster Aggregation
        ?
Analysis Dashboard
```

## Architecture

```text
ResumeMatch/
+-- app/               # FastAPI backend & analysis engine
¦   +-- analysis/      # Matching, scoring, & logic
¦   +-- api/           # Endpoints
¦   +-- config/        # Thresholds & taxonomy
¦   +-- models/        # Schemas
+-- frontend/          # Next.js dashboard
+-- tests/             # Engine & API tests
```

## Matching Model

We use cosine similarity to identify potential evidence for requirements.

| Threshold | Value | Purpose |
|---|---:|---|
| **Evidence** | 0.35 | Filters insufficient semantic evidence |
| **Partial** | 0.30 | Relevant but incomplete evidence |
| **Strong** | 0.60 | Evidence clearly satisfies requirement |

*Note: Thresholds were empirically calibrated against benchmark v1.0.0 and are not claimed to be universally optimal.*

## Evaluation

| Metric | Baseline | Calibrated |
|---|---:|---:|
| Accuracy | 71.43% | **82.86%** |
| Macro F1 | 0.666 | **0.777** |
| False Strong | — | **0** |

## Local Development

### Backend
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
Navigate to `frontend/`, copy `.env.example` to `.env.local` (configure `NEXT_PUBLIC_API_URL`), then:
```bash
npm install
npm run dev
```

## API
- `GET /health`
- `POST /api/analyze`

## Testing
```bash
pytest
npm run build
```

## Limitations
- Performance with specialized technical relationships depends on the `MiniLM` model training data.
- Relies on structured text inputs (no PDF/DOCX parsing).
- Calibration is based on a focused 35-case benchmark.

## Roadmap — Not Implemented
- PDF/DOCX resume parsing
- Analysis history / user accounts
- Downloadable PDF reports
- Broader industry-specific taxonomies

---

Built with: **Python** · **FastAPI** · **Sentence Transformers** · **Next.js** · **TypeScript** · **Tailwind CSS**
