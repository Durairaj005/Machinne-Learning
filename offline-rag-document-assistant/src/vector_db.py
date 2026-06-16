"""FAISS vector database helpers."""

import json
import os
from typing import Dict, List

import faiss
import numpy as np


def _normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """Normalize embeddings so inner product behaves like cosine similarity."""
    normalized = embeddings.copy().astype(np.float32)
    faiss.normalize_L2(normalized)
    return normalized


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """Create and populate a FAISS index."""
    if embeddings.size == 0:
        raise ValueError("Embeddings are empty. Cannot build index.")

    normalized = _normalize_embeddings(embeddings)
    dimension = normalized.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(normalized)
    return index


def save_index(index: faiss.Index, index_path: str) -> None:
    """Persist FAISS index to disk."""
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    faiss.write_index(index, index_path)


def load_index(index_path: str) -> faiss.Index:
    """Load FAISS index from disk."""
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index not found at: {index_path}")
    return faiss.read_index(index_path)


def save_chunks(chunks: List[Dict[str, object]], chunks_path: str) -> None:
    """Save chunk metadata as JSON."""
    os.makedirs(os.path.dirname(chunks_path), exist_ok=True)
    with open(chunks_path, "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)


def load_chunks(chunks_path: str) -> List[Dict[str, object]]:
    """Load chunk metadata from JSON."""
    if not os.path.exists(chunks_path):
        raise FileNotFoundError(f"Chunk file not found at: {chunks_path}")

    with open(chunks_path, "r", encoding="utf-8") as file:
        return json.load(file)


def search_similar_chunks(
    index: faiss.Index,
    query_embedding: np.ndarray,
    chunks: List[Dict[str, object]],
    top_k: int = 3,
) -> List[Dict[str, object]]:
    """Search for the most relevant chunks and return text with similarity scores."""
    if query_embedding.size == 0:
        raise ValueError("Query embedding is empty.")
    if not chunks:
        raise ValueError("Chunk list is empty.")

    k = max(1, min(top_k, len(chunks)))

    normalized_query = _normalize_embeddings(query_embedding)
    scores, indices = index.search(normalized_query, k)

    results: List[Dict[str, object]] = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk_data = chunks[idx]
        results.append(
            {
                "chunk_text": chunk_data.get("chunk_text", ""),
                "score": float(score),
                "index": int(idx),
                "file_name": chunk_data.get("file_name", "unknown.pdf"),
                "page_number": chunk_data.get("page_number", 0),
                "chunk_id": chunk_data.get("chunk_id", idx + 1),
            }
        )

    return results
