from fastapi import APIRouter, Depends, HTTPException

from app.analysis.pipeline import AnalysisPipeline
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import build_pipeline
from app.services.mapper import to_response

router = APIRouter()


def get_pipeline() -> AnalysisPipeline:
    return build_pipeline()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    payload: AnalyzeRequest,
    pipeline: AnalysisPipeline = Depends(get_pipeline),
) -> AnalyzeResponse:
    result = pipeline.analyze(payload.resume, payload.job_description)
    if not result.job_chunks:
        raise HTTPException(
            status_code=422,
            detail="Could not extract any job requirements. Provide a more detailed job description.",
        )
    return to_response(result)
