"""Embedding utilities built on SentenceTransformers."""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"


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
    """Generate a single query embedding with model-specific retrieval prefix."""
    # BGE models use an asymmetric query prompt for superior passage retrieval
    model_str = str(model).lower() + " " + getattr(model, "name_or_path", "").lower()
    prefix = ""
    if "bge" in model_str:
        prefix = "Represent this sentence for searching relevant passages: "

    formatted_query = prefix + query if prefix else query
    vector = model.encode([formatted_query], convert_to_numpy=True, show_progress_bar=False)
    return vector.astype(np.float32)
