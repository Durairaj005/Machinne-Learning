"""Text chunking helpers for RAG pipelines."""

from typing import Dict, List


def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks using word counts.

    Args:
        text: Source text.
        chunk_size: Target number of words per chunk.
        overlap: Number of words to overlap between neighboring chunks.

    Returns:
        List of chunk strings.

    Raises:
        ValueError: If chunking configuration is invalid.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if overlap < 0:
        raise ValueError("overlap cannot be negative.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    words = text.split()
    if not words:
        return []

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk_words = words[start:end]
        if not chunk_words:
            continue
        chunks.append(" ".join(chunk_words))

        if end >= len(words):
            break

    return chunks


def split_pages_into_chunks(
    pages: List[Dict[str, object]],
    chunk_size: int = 500,
    overlap: int = 50,
    starting_chunk_id: int = 1,
) -> List[Dict[str, object]]:
    """Split each page into overlapping metadata-rich chunks.

    Returns chunk dictionaries with:
    - file_name
    - page_number
    - chunk_id
    - chunk_text
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")
    if overlap < 0:
        raise ValueError("overlap cannot be negative.")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    chunked_pages: List[Dict[str, object]] = []
    current_chunk_id = starting_chunk_id
    step = chunk_size - overlap

    for page in pages:
        text = str(page.get("page_text", "")).strip()
        if not text:
            continue

        words = text.split()
        for start in range(0, len(words), step):
            end = start + chunk_size
            chunk_words = words[start:end]
            if not chunk_words:
                continue

            chunked_pages.append(
                {
                    "file_name": page.get("file_name", "unknown.pdf"),
                    "page_number": int(page.get("page_number", 0)),
                    "chunk_id": current_chunk_id,
                    "chunk_text": " ".join(chunk_words),
                }
            )
            current_chunk_id += 1

            if end >= len(words):
                break

    return chunked_pages
