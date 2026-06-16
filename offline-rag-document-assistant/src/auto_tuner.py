"""Automatic setting recommendations for chunking and retrieval."""

from typing import Dict, Tuple


def recommend_chunk_settings(total_pdfs: int, total_bytes: int) -> Tuple[int, int]:
    """Recommend chunk size and overlap from upload volume.

    Larger uploads use larger chunks for faster indexing, while smaller uploads
    use smaller chunks for better granularity.
    """
    total_mb = total_bytes / (1024 * 1024)

    if total_pdfs >= 4 or total_mb >= 10:
        return 650, 100
    if total_pdfs >= 2 or total_mb >= 3:
        return 550, 80
    if total_mb <= 0.8:
        return 380, 50

    return 500, 60


def recommend_chunk_settings_for_document(total_words: int, page_count: int = 1) -> Dict[str, int]:
    """Recommend chunking settings using the total number of words in a document.

    The goal is to use smaller chunks for short documents and larger chunks for
    longer documents, so the index stays compact but still preserves context.
    """
    if total_words <= 0:
        return {"chunk_size": 200, "overlap": 20}

    if total_words <= 250:
        chunk_size, overlap = 180, 0
    elif total_words <= 600:
        chunk_size, overlap = 220, 30
    elif total_words <= 1_200:
        chunk_size, overlap = 300, 40
    elif total_words <= 2_500:
        chunk_size, overlap = 420, 60
    elif total_words <= 5_000:
        chunk_size, overlap = 550, 80
    elif total_words <= 10_000:
        chunk_size, overlap = 700, 100
    else:
        chunk_size, overlap = 800, 120

    # Slightly increase chunk size for multi-page documents to reduce fragmentation.
    if page_count >= 5 and chunk_size < 700:
        chunk_size += 40

    # Ensure overlap always stays smaller than chunk size.
    overlap = min(overlap, max(0, chunk_size - 1))

    return {"chunk_size": chunk_size, "overlap": overlap}


def recommend_retrieval_settings(
    question: str,
    query_type: str,
    total_chunks: int,
    default_top_k: int = 3,
    default_min_similarity: float = 0.45,
) -> Tuple[int, float]:
    """Recommend Top-K and minimum similarity from query intent.

    Broad questions (summary/comparison) need more chunks.
    Direct factual questions are stricter and use fewer chunks.
    """
    normalized_question = question.strip().lower()
    q_word_count = len(normalized_question.split())

    top_k = default_top_k
    min_similarity = default_min_similarity

    if query_type == "Summary Question":
        top_k = 5
        min_similarity = 0.35
    elif query_type == "Comparison Question":
        top_k = 4
        min_similarity = 0.38
    elif query_type == "Definition Question":
        top_k = 2
        min_similarity = 0.50
    elif query_type == "Direct Fact Question":
        top_k = 2
        min_similarity = 0.52
    elif query_type == "Unknown Question":
        top_k = 3
        min_similarity = 0.55

    # Very short questions are often ambiguous, so use a stricter threshold.
    if q_word_count <= 4:
        min_similarity = min(min_similarity + 0.05, 0.70)

    # Clamp settings to safe bounds and current index size.
    safe_top_k = max(1, min(top_k, max(1, total_chunks), 8))
    safe_similarity = max(0.20, min(min_similarity, 0.80))

    return safe_top_k, safe_similarity
