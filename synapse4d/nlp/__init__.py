"""Natural Language Processing and Polarity Module for Synapse 4D."""

from .polarity import (
    CANONICAL_ANTONYMS,
    NEGATION_MARKERS,
    detect_polarity,
    has_polar_opposition,
    classify_relation,
)
from .embeddings import (
    DEFAULT_MODEL_NAME,
    EmbeddingEngine,
    get_embedding,
    compute_similarity,
)

__all__ = [
    "CANONICAL_ANTONYMS",
    "NEGATION_MARKERS",
    "detect_polarity",
    "has_polar_opposition",
    "classify_relation",
    "DEFAULT_MODEL_NAME",
    "EmbeddingEngine",
    "get_embedding",
    "compute_similarity",
]
