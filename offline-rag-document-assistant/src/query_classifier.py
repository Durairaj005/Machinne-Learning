"""Rule-based query type classifier for user questions."""


def classify_query(question: str) -> str:
    """Classify query intent into simple interview-friendly categories."""
    normalized = question.strip().lower()
    if not normalized:
        return "Unknown Question"

    if normalized.startswith(("what is", "define")):
        return "Definition Question"

    if "summarize" in normalized or "summary" in normalized:
        return "Summary Question"

    if "compare" in normalized or "difference" in normalized or "versus" in normalized:
        return "Comparison Question"

    if normalized.startswith(("who", "when", "where", "how many")):
        return "Direct Fact Question"

    return "Unknown Question"
