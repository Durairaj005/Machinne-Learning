"""Main RAG pipeline orchestration."""

import os
import time
from typing import Dict, List

from src.embeddings import generate_embeddings, generate_query_embedding, load_embedding_model
from src.auto_tuner import recommend_chunk_settings_for_document
from src.ollama_llm import generate_answer_with_ollama
from src.pdf_reader import extract_text_by_page
from src.text_splitter import split_pages_into_chunks
from src.vector_db import build_faiss_index, save_chunks, save_index, search_similar_chunks


def _tokenize_for_overlap(text: str) -> List[str]:
    """Simple tokenizer for lightweight lexical reranking."""
    cleaned = text.lower()
    for char in ",.;:!?()[]{}\"'\n\t":
        cleaned = cleaned.replace(char, " ")
    return [token for token in cleaned.split() if len(token) > 2]


def _get_query_keywords(question: str) -> List[str]:
    """Build keyword list with a few RAG-friendly intent synonyms."""
    stop_words = {
        "what",
        "which",
        "where",
        "when",
        "who",
        "the",
        "this",
        "that",
        "from",
        "with",
        "about",
        "into",
        "pdf",
        "document",
        "main",
    }

    tokens = [token for token in _tokenize_for_overlap(question) if token not in stop_words]

    # Add a small synonym expansion for "purpose/goal"-style questions.
    if any(word in tokens for word in ["purpose", "goal", "objective"]):
        tokens.extend(["role", "objective", "responsibility", "job", "type", "intern"])

    return list(dict.fromkeys(tokens))


def _rerank_retrieved_chunks(question: str, retrieved: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """Rerank chunks with semantic score + lexical overlap for better grounding."""
    if not retrieved:
        return []

    query_keywords = _get_query_keywords(question)
    if not query_keywords:
        return retrieved

    max_overlap = max(1, len(query_keywords))
    reranked: List[Dict[str, object]] = []

    for item in retrieved:
        chunk_text = str(item.get("chunk_text", ""))
        chunk_tokens = set(_tokenize_for_overlap(chunk_text))
        overlap_count = sum(1 for keyword in query_keywords if keyword in chunk_tokens)
        lexical_score = overlap_count / max_overlap

        semantic_score = float(item.get("score", 0.0))
        # Heuristic blend: semantic similarity remains primary signal.
        combined_score = (0.80 * semantic_score) + (0.20 * lexical_score)

        new_item = dict(item)
        new_item["combined_score"] = combined_score
        reranked.append(new_item)

    reranked.sort(key=lambda row: float(row.get("combined_score", 0.0)), reverse=True)
    return reranked


def process_pdfs(
    uploaded_pdfs: List[Dict[str, object]],
    vector_store_dir: str = "vector_store",
    chunk_size: int = 500,
    overlap: int = 50,
    embedding_model_name: str = "all-MiniLM-L6-v2",
    auto_optimize: bool = True,
) -> Dict[str, object]:
    """Build embeddings and a FAISS index from one or more uploaded PDFs."""
    if not uploaded_pdfs:
        raise ValueError("Please upload at least one PDF file.")

    all_pages: List[Dict[str, object]] = []
    all_chunks: List[Dict[str, object]] = []
    file_settings: List[Dict[str, object]] = []
    current_chunk_id = 1

    for pdf in uploaded_pdfs:
        file_name = str(pdf.get("file_name", "unknown.pdf"))
        pdf_bytes = pdf.get("pdf_bytes")
        if not isinstance(pdf_bytes, (bytes, bytearray)):
            raise ValueError(f"Invalid PDF bytes for {file_name}.")

        pages = extract_text_by_page(bytes(pdf_bytes), file_name=file_name)
        all_pages.extend(pages)

        total_words = sum(len(str(page.get("page_text", "")).split()) for page in pages)
        if auto_optimize:
            tuned = recommend_chunk_settings_for_document(total_words=total_words, page_count=len(pages))
            selected_chunk_size = tuned["chunk_size"]
            selected_overlap = tuned["overlap"]
        else:
            selected_chunk_size = chunk_size
            selected_overlap = overlap

        file_settings.append(
            {
                "file_name": file_name,
                "page_count": len(pages),
                "word_count": total_words,
                "chunk_size": selected_chunk_size,
                "overlap": selected_overlap,
            }
        )

        page_chunks = split_pages_into_chunks(
            pages=pages,
            chunk_size=selected_chunk_size,
            overlap=selected_overlap,
            starting_chunk_id=current_chunk_id,
        )
        all_chunks.extend(page_chunks)
        current_chunk_id += len(page_chunks)

    if not all_chunks:
        raise ValueError("Could not create chunks from the uploaded PDF files.")

    model = load_embedding_model(embedding_model_name)
    chunk_texts = [chunk["chunk_text"] for chunk in all_chunks]
    chunk_embeddings = generate_embeddings(model, chunk_texts)
    index = build_faiss_index(chunk_embeddings)

    os.makedirs(vector_store_dir, exist_ok=True)
    index_path = os.path.join(vector_store_dir, "document_index.faiss")
    chunks_path = os.path.join(vector_store_dir, "document_chunks.json")

    save_index(index, index_path)
    save_chunks(all_chunks, chunks_path)

    return {
        "chunks": all_chunks,
        "pages": all_pages,
        "embedding_model": model,
        "index": index,
        "index_path": index_path,
        "chunks_path": chunks_path,
        "total_pdfs": len(uploaded_pdfs),
        "file_settings": file_settings,
    }


def answer_question(
    question: str,
    index,
    chunks: List[Dict[str, object]],
    embedding_model,
    query_type: str,
    ollama_model_name: str = "llama3.2",
    top_k: int = 3,
    min_similarity_for_answer: float = 0.45,
) -> Dict[str, object]:
    """Retrieve relevant chunks and ask Ollama to generate an answer."""
    start_time = time.perf_counter()

    query_embedding = generate_query_embedding(embedding_model, question)
    # Retrieve a wider candidate pool first, then rerank and keep final top_k.
    candidate_k = max(top_k, 4)
    retrieved_candidates = search_similar_chunks(
        index=index,
        query_embedding=query_embedding,
        chunks=chunks,
        top_k=candidate_k,
    )

    reranked_candidates = _rerank_retrieved_chunks(question=question, retrieved=retrieved_candidates)
    retrieved = reranked_candidates[: max(1, top_k)]

    top_similarity = retrieved[0]["score"] if retrieved else 0.0
    average_similarity = sum(item["score"] for item in retrieved) / len(retrieved) if retrieved else 0.0

    # Guardrail: avoid approximate or hallucinated answers when retrieval quality is weak.
    if top_similarity < min_similarity_for_answer:
        response_time = time.perf_counter() - start_time
        return {
            "answer": "I could not find this information in the uploaded document.",
            "retrieved_chunks": retrieved,
            "response_time": response_time,
            "top_similarity_scores": [item["score"] for item in retrieved],
            "average_similarity_score": average_similarity,
            "confidence_level": "Answer not found in document",
        }

    context_chunks = [item["chunk_text"] for item in retrieved]
    answer = generate_answer_with_ollama(
        question=question,
        context_chunks=context_chunks,
        query_type=query_type,
        model_name=ollama_model_name,
    )

    response_time = time.perf_counter() - start_time

    if top_similarity >= 0.65:
        confidence_level = "High Confidence"
    elif top_similarity >= 0.45:
        confidence_level = "Medium Confidence"
    elif top_similarity >= 0.25:
        confidence_level = "Low Confidence"
    else:
        confidence_level = "Answer not found in document"

    return {
        "answer": answer,
        "retrieved_chunks": retrieved,
        "response_time": response_time,
        "top_similarity_scores": [item["score"] for item in retrieved],
        "average_similarity_score": average_similarity,
        "confidence_level": confidence_level,
    }
