"""Shared test fixtures. Tests use HashingEmbedder so they never download MiniLM."""

from __future__ import annotations

import pytest

from app.analysis.embeddings import HashingEmbedder
from app.analysis.pipeline import AnalysisPipeline
from app.analysis.taxonomy import load_taxonomy


@pytest.fixture
def pipeline() -> AnalysisPipeline:
    return AnalysisPipeline(
        embedder=HashingEmbedder(dim=96),
        taxonomy=load_taxonomy(),
        strong_threshold=0.65,
        partial_threshold=0.40,
        min_chunk_chars=20,
        max_chunk_chars=420,
    )
