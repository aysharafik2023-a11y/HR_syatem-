"""PDF resume parser using pypdf."""

from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text content from a PDF file."""
    reader = PdfReader(str(file_path))
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    text = "\n".join(text_parts).strip()
    if not text:
        raise ValueError(f"Could not extract text from PDF: {file_path.name}")
    return text
