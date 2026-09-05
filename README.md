# Resume-to-Job-Match Analyzer

Semantic resume-to-job alignment with **skill-cluster gap analysis**. This repository currently contains the V1 backend: a FastAPI service wrapping an independent analysis engine.

## Current architecture

```text
resume  → preprocess → evidence chunks
job     → preprocess → requirement chunks
                ↓
     sentence embeddings
                ↓
  requirement ↔ evidence cosine match
                ↓
     skill-cluster assignment
                ↓
 cluster scores → gap explanations → API JSON
```

```text
app/
  main.py                 FastAPI app factory, CORS, health, embedder warmup
  api/routes.py           POST /api/analyze
  models/schemas.py       Pydantic request/response contracts for a future Next.js client
  services/analyzer.py    Composition root (settings + taxonomy + embedder → pipeline)
  services/mapper.py      AnalysisResult → API response
  analysis/               Framework-free analysis engine
    preprocessing.py      Chunking, headers, de-duplication
    embeddings.py         Embedder interface + MiniLM implementation
    matching.py           Cosine similarity, best evidence, cluster assignment
    scoring.py            Thresholds, cluster scores, overall score
    explanations.py       Deterministic evidence-backed templates
    taxonomy.py           Loads skill clusters from JSON
    pipeline.py           Orchestrates the flow above
    types.py              Dataclasses returned by the engine
  config/
    settings.py           Thresholds and model name (env: RTJ_*)
    skill_taxonomy.json   Extensible cluster taxonomy
tests/                    Engine and API tests (no MiniLM download)
```

## Decisions locked for V1

1. **Engine ≠ API.** `app.analysis` has no FastAPI imports. Tests can run the pipeline with a fake embedder.
2. **Requirement-centric matching.** Each job chunk is matched to its strongest resume chunk. Document-level cosine similarity is not the product metric.
3. **Taxonomy is data.** Clusters live in `app/config/skill_taxonomy.json`. Add or edit clusters there; do not scatter skill lists through Python.
4. **Explanations are templates.** V1 does not call an LLM. Every explanation cites a requirement, evidence, score, cluster, and status.
5. **Thresholds are calibration knobs.** `strong` / `partial` / `weak` cutoffs are settings, not scientific constants.
6. **Only JD-relevant clusters are scored.** A cluster appears in the response if at least one job requirement was assigned to it.
7. **Embedder is injectable.** Production uses `sentence-transformers/all-MiniLM-L6-v2`. Tests use a deterministic hashing embedder.

## API

`POST /api/analyze`

```json
{
  "resume": "plain text...",
  "job_description": "plain text..."
}
```

Response includes overall score (0–100), summary, skill clusters (score, status, matched vs weak requirements), evidence lists, and explanations.

`GET /health` returns `{"status": "ok"}`.

Interactive docs: `http://127.0.0.1:8000/docs`

## Setup

Python 3.11+ recommended.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run the API

Copy the root `.env.example` to `.env` to override default thresholds or CORS settings.

```bash
uvicorn app.main:app --reload
```

The first production start downloads MiniLM (~80MB) and warms the model.

### Run tests

```bash
pytest
```

## Deployment

### Backend (FastAPI)
- Uses `uvicorn` as the server.
- The `render.yaml` file defines the deployment configuration.
- Set environment variables as defined in `.env.example`.

### Frontend (Next.js)
1. Navigate to the `frontend/` directory.
2. Copy `frontend/.env.example` to `frontend/.env.local`.
3. Set `NEXT_PUBLIC_API_URL` to your backend production URL.
4. Run `npm install` and `npm run build`.

## Next milestone

- Calibrate thresholds against labeled resume/JD pairs
- Optional PDF/DOCX text extraction
