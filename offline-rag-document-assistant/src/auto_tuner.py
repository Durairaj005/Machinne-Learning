"""Automatic setting recommendations for chunking and retrieval."""

from typing import Dict, Tuple


def recommend_chunk_settings(total_pdfs: int, total_bytes: int) -> Tuple[int, int]:
    """Recommend chunk size and overlap from upload volume.

    Smaller chunk sizes preserve fine-grained details such as resume skills and bullet points.
    """
    total_mb = total_bytes / (1024 * 1024)

    if total_pdfs >= 4 or total_mb >= 10:
        return 500, 80
    if total_pdfs >= 2 or total_mb >= 3:
        return 400, 60
    if total_mb <= 0.8:
        return 300, 50

    return 350, 50


def recommend_chunk_settings_for_document(total_words: int, page_count: int = 1) -> Dict[str, int]:
    """Recommend chunking settings using the total number of words in a document."""
    if total_words <= 0:
        return {"chunk_size": 200, "overlap": 30}

    if total_words <= 300:
        chunk_size, overlap = 200, 30
    elif total_words <= 800:
        chunk_size, overlap = 250, 40
    elif total_words <= 1_500:
        chunk_size, overlap = 300, 50
    elif total_words <= 3_000:
        chunk_size, overlap = 380, 60
    elif total_words <= 6_000:
        chunk_size, overlap = 450, 70
    else:
        chunk_size, overlap = 550, 80

    overlap = min(overlap, max(0, chunk_size - 1))
    return {"chunk_size": chunk_size, "overlap": overlap}


def recommend_retrieval_settings(
    question: str,
    query_type: str,
    total_chunks: int,
    default_top_k: int = 3,
    default_min_similarity: float = 0.25,
) -> Tuple[int, float]:
    """Recommend Top-K and minimum similarity from query intent."""
    top_k = default_top_k
    min_similarity = default_min_similarity

    if query_type in ["Extraction / Skills Question", "Summary Question"]:
        top_k = 4
        min_similarity = 0.20
    elif query_type == "Comparison Question":
        top_k = 4
        min_similarity = 0.22
    elif query_type == "Definition Question":
        top_k = 3
        min_similarity = 0.25
    elif query_type == "Direct Fact Question":
        top_k = 3
        min_similarity = 0.25
    else:
        top_k = 3
        min_similarity = 0.22

    safe_top_k = max(1, min(top_k, max(1, total_chunks), 8))
    safe_similarity = max(0.15, min(min_similarity, 0.60))

    return safe_top_k, safe_similarity
