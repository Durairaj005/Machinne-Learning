"""Rule-based query type classifier for user questions."""


def classify_query(question: str) -> str:
    """Classify query intent into simple interview-friendly categories."""
    normalized = question.strip().lower()
    if not normalized:
        return "Unknown Question"

    # Profile, skill, experience, or attribute extraction
    if any(keyword in normalized for keyword in ["skill", "skills", "experience", "education", "project", "background", "technolog", "qualification", "certification"]):
        return "Extraction / Skills Question"

    if "summarize" in normalized or "summary" in normalized or "overview" in normalized:
        return "Summary Question"

    if "compare" in normalized or "difference" in normalized or "versus" in normalized or "vs" in normalized:
        return "Comparison Question"

    if normalized.startswith(("who", "when", "where", "how many", "which")):
        return "Direct Fact Question"

    if normalized.startswith(("what is", "define")):
        return "Definition Question"

    return "Information Query"
