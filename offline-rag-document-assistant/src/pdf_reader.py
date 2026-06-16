"""Utilities for reading PDF documents with PyMuPDF."""

from typing import Dict, List

import fitz


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a PDF file represented as bytes.

    Args:
        pdf_bytes: Raw PDF bytes.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the PDF is empty or text extraction fails.
    """
    if not pdf_bytes:
        raise ValueError("No PDF data received.")

    try:
        text_parts = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            if document.page_count == 0:
                raise ValueError("The uploaded PDF has no pages.")

            for page in document:
                page_text = page.get_text("text")
                if page_text:
                    text_parts.append(page_text)

        full_text = "\n".join(text_parts).strip()
        if not full_text:
            raise ValueError("No readable text found in this PDF.")

        return full_text
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Failed to read PDF: {exc}") from exc


def extract_text_by_page(pdf_bytes: bytes, file_name: str) -> List[Dict[str, object]]:
    """Extract non-empty text from each PDF page with metadata.

    Args:
        pdf_bytes: Raw PDF bytes.
        file_name: Name of the uploaded PDF.

    Returns:
        A list of dictionaries containing file_name, page_number, and page_text.

    Raises:
        ValueError: If PDF cannot be parsed or contains no readable text.
    """
    if not pdf_bytes:
        raise ValueError("No PDF data received.")

    try:
        pages: List[Dict[str, object]] = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            if document.page_count == 0:
                raise ValueError(f"{file_name} has no pages.")

            for page_idx, page in enumerate(document, start=1):
                page_text = page.get_text("text").strip()
                if not page_text:
                    continue
                pages.append(
                    {
                        "file_name": file_name,
                        "page_number": page_idx,
                        "page_text": page_text,
                    }
                )

        if not pages:
            raise ValueError(f"No readable text found in {file_name}.")

        return pages
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"Failed to read PDF {file_name}: {exc}") from exc
