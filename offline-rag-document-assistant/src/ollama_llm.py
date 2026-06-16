"""Local Ollama LLM client."""

from typing import List

import requests


OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"


def _build_prompt(context_chunks: List[str], question: str, query_type: str) -> str:
    context_text = "\n\n".join(context_chunks)
    return (
        "You are an AI document assistant.\n"
        "Answer the user question only using the provided context.\n\n"
        f"Question Type:\n{query_type}\n\n"
        f"Context:\n{context_text}\n\n"
        f"User Question:\n{question}\n\n"
        "Rules:\n"
        "1. If the answer is available in the context, answer clearly.\n"
        "2. If the answer is not available in the context, say:\n"
        '"I could not find this information in the uploaded document."\n'
        "3. Do not give answers from outside knowledge.\n"
        "4. Keep the answer simple and beginner-friendly.\n"
        "5. Mention that the answer is based on the retrieved document content.\n"
    )


def generate_answer_with_ollama(
    question: str,
    context_chunks: List[str],
    query_type: str,
    model_name: str = "llama3.2",
    endpoint: str = OLLAMA_ENDPOINT,
    timeout: int = 120,
) -> str:
    """Generate an answer using a local Ollama model."""
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    prompt = _build_prompt(context_chunks, question, query_type)
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "").strip()

        if not answer:
            return "I could not generate an answer. Please try again."

        return answer
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Could not connect to Ollama. Make sure Ollama is installed and running on localhost:11434."
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise RuntimeError("Ollama request timed out. Please try again.") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc
