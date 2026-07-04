"""Base resume parser that dispatches to format-specific parsers."""

from pathlib import Path

from hr_system.parsers.docx_parser import extract_text_from_docx
from hr_system.parsers.pdf_parser import extract_text_from_pdf


def parse_resume(file_path: str | Path) -> str:
    """Parse a resume file and extract text content.

    Supports PDF and DOCX formats.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    elif suffix == ".docx":
        return extract_text_from_docx(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported: .pdf, .docx")
