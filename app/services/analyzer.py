"""Composition root for the analysis engine."""

from __future__ import annotations

from functools import lru_cache

from app.analysis.embeddings import Embedder, MiniLMEmbedder
from app.analysis.pipeline import AnalysisPipeline
from app.analysis.taxonomy import load_taxonomy
from app.analysis.types import AnalysisConfig
from app.config.settings import Settings, get_settings


@lru_cache(maxsize=1)
def get_embedder() -> Embedder:
    settings = get_settings()
    return MiniLMEmbedder(settings.embedding_model)


def build_pipeline(embedder: Embedder | None = None, settings: Settings | None = None) -> AnalysisPipeline:
    active_settings = settings or get_settings()
    config = AnalysisConfig(
        strong_threshold=active_settings.strong_threshold,
        partial_threshold=active_settings.partial_threshold,
        min_chunk_chars=active_settings.min_chunk_chars,
        max_chunk_chars=active_settings.max_chunk_chars,
    )
    return AnalysisPipeline(
        embedder=embedder or get_embedder(),
        taxonomy=load_taxonomy(),
        config=config,
    )
