"""Embedding utilities built on SentenceTransformers."""

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL) -> SentenceTransformer:
    """Load and return a SentenceTransformers model."""
    return SentenceTransformer(model_name)


def generate_embeddings(model: SentenceTransformer, texts: List[str]) -> np.ndarray:
    """Generate embeddings for a list of texts."""
    if not texts:
        return np.empty((0, 0), dtype=np.float32)

    vectors = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return vectors.astype(np.float32)


def generate_query_embedding(model: SentenceTransformer, query: str) -> np.ndarray:
    """Generate a single query embedding."""
    vector = model.encode([query], convert_to_numpy=True, show_progress_bar=False)
    return vector.astype(np.float32)
