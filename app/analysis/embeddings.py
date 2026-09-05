"""Embedding interface. The analysis engine depends on this, not on FastAPI or a specific model class."""

from __future__ import annotations

import zlib
from abc import ABC, abstractmethod
from collections.abc import Sequence

import numpy as np


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: Sequence[str]) -> np.ndarray:
        """Return an array of shape (n_texts, dim). Empty input returns shape (0, dim)."""


class MiniLMEmbedder(Embedder):
    """Production embedder backed by sentence-transformers/all-MiniLM-L6-v2 (or a configured equivalent)."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        dim_fn = getattr(self._model, "get_sentence_embedding_dimension", None) or getattr(self._model, "get_embedding_dimension", None)
        self.dim = int(dim_fn()) if dim_fn else 384

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        vectors = self._model.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(vectors, dtype=np.float32)


class HashingEmbedder(Embedder):
    """Deterministic token-overlap embedder for tests. Not used in production."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            tokens = _tokenize(text)
            for token in tokens:
                matrix[row, zlib.crc32(token.encode("utf-8")) % self.dim] += 1.0
            norm = np.linalg.norm(matrix[row])
            if norm > 0:
                matrix[row] /= norm
        return matrix


def _tokenize(text: str) -> list[str]:
    return [token for token in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if token]
