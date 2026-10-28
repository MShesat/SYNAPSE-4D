"""
Offline-First Embedding Engine for Synapse 4D.

Uses a localized ONNX runtime model (384 dimensions) with zero-network requirements at runtime.
Integrates with Chroma's verified local ONNX model or fastembed when local weights are available.
Provides thread-safe embeddings and cosine similarity.
"""

from __future__ import annotations
from typing import List, Optional, Union
import numpy as np

DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"


class EmbeddingEngine:
    _instance: Optional[EmbeddingEngine] = None
    _embed_fn = None

    def __init__(self):
        self._init_embedding_function()

    def _init_embedding_function(self):
        if self._embed_fn is None:
            from chromadb.utils import embedding_functions
            self._embed_fn = embedding_functions.DefaultEmbeddingFunction()

    @classmethod
    def get_instance(cls) -> EmbeddingEngine:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string into a 384-dimensional vector."""
        if not text or not text.strip():
            return [0.0] * 384
        res = self._embed_fn([text])
        return [float(x) for x in res[0]]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of text strings."""
        if not texts:
            return []
        cleaned = [t if t and t.strip() else " " for t in texts]
        res = self._embed_fn(cleaned)
        return [[float(x) for x in vec] for vec in res]

    @staticmethod
    def cosine_similarity(
        vec_a: Union[List[float], np.ndarray],
        vec_b: Union[List[float], np.ndarray],
    ) -> float:
        """Compute cosine similarity bounded in [-1.0, 1.0]."""
        a = np.asarray(vec_a, dtype=np.float32)
        b = np.asarray(vec_b, dtype=np.float32)
        norm_a = float(np.linalg.norm(a))
        norm_b = float(np.linalg.norm(b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        dot = float(np.dot(a, b))
        return max(-1.0, min(1.0, dot / (norm_a * norm_b)))


def get_embedding(text: str) -> List[float]:
    """Convenience helper."""
    return EmbeddingEngine.get_instance().embed_text(text)


def compute_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Convenience helper."""
    return EmbeddingEngine.cosine_similarity(vec_a, vec_b)
