"""
app/ml/resume_parser.py
------------------------
Extracts raw text from PDF and DOCX resume files.

PDF  → pdfplumber  (handles multi-column layouts, tables)
DOCX → python-docx (reads paragraphs + tables)
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# PDF
# ─────────────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file using pdfplumber.
    Returns an empty string on failure rather than raising so the upload
    pipeline can still create a Candidate record with partial data.
    """
    try:
        import pdfplumber  # imported here so tests can mock it
        text_parts: list[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if page_text:
                    text_parts.append(page_text)
        raw = "\n".join(text_parts)
        return _clean_extracted_text(raw)
    except Exception as exc:
        logger.warning("PDF extraction failed for %s: %s", file_path, exc)
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# DOCX
# ─────────────────────────────────────────────────────────────────────────────

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract all text from a DOCX file using python-docx.
    Reads body paragraphs AND table cells so structured resumes are covered.
    """
    try:
        from docx import Document  # type: ignore
        doc = Document(file_path)
        parts: list[str] = []

        # Body paragraphs
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                parts.append(text)

        # Tables (many resumes use tables for layout)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text = cell.text.strip()
                    if text:
                        parts.append(text)

        raw = "\n".join(parts)
        return _clean_extracted_text(raw)
    except Exception as exc:
        logger.warning("DOCX extraction failed for %s: %s", file_path, exc)
        return ""


# ─────────────────────────────────────────────────────────────────────────────
# Dispatcher
# ─────────────────────────────────────────────────────────────────────────────

def extract_text(file_path: str) -> str:
    """
    Route to the correct extractor based on file extension.
    Raises ValueError for unsupported extensions.
    """
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    raise ValueError(f"Unsupported file type: {ext}")


# ─────────────────────────────────────────────────────────────────────────────
# Post-extraction cleanup
# ─────────────────────────────────────────────────────────────────────────────

def _clean_extracted_text(text: str) -> str:
    """
    Light cleanup after raw extraction:
    - Collapse 3+ consecutive blank lines to 2
    - Normalise unicode whitespace / non-breaking spaces
    - Strip leading/trailing whitespace per line
    """
    # normalise non-breaking spaces and similar unicode whitespace
    text = text.replace("\u00a0", " ").replace("\u2019", "'").replace("\u2013", "-")
    # strip trailing spaces per line
    lines = [line.rstrip() for line in text.splitlines()]
    # collapse runs of blank lines
    cleaned: list[str] = []
    blank_run = 0
    for line in lines:
        if line == "":
            blank_run += 1
            if blank_run <= 2:
                cleaned.append(line)
        else:
            blank_run = 0
            cleaned.append(line)
    return "\n".join(cleaned).strip()


# ─────────────────────────────────────────────────────────────────────────────
# Contact info extraction (regex-based, no external NLP dependency)
# ─────────────────────────────────────────────────────────────────────────────

def extract_email(text: str) -> str | None:
    """Return the first email address found in the text."""
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group(0).lower() if match else None


def extract_phone(text: str) -> str | None:
    """Return the first phone number found in the text."""
    pattern = r"(\+?\d[\d\s\-().]{7,}\d)"
    match = re.search(pattern, text)
    if match:
        phone = re.sub(r"[\s\-().]+", "-", match.group(0)).strip("-")
        return phone
    return None


def extract_name_heuristic(text: str) -> str:
    """
    Heuristic: the candidate's name is usually the first non-empty line
    that looks like a proper name (Title Case, 2-4 words, no digits).
    Falls back to 'Unknown Candidate'.
    """
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Skip lines with URLs, emails, numbers
        if any(c in line for c in ["@", "http", "www", "/", "\\"]):
            continue
        if re.search(r"\d", line):
            continue
        words = line.split()
        if 2 <= len(words) <= 5 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
    return "Unknown Candidate"


def extract_experience_years(text: str) -> float:
    """
    Try to parse total years of experience from common patterns like:
      '5 years of experience', '3+ years', '2-4 years experience'
    Returns 0.0 if nothing found.
    """
    patterns = [
        r"(\d+)\+?\s+years?\s+of\s+experience",
        r"(\d+)\+?\s+years?\s+experience",
        r"experience\s+of\s+(\d+)\+?\s+years?",
        r"(\d+)\s*[-–]\s*\d+\s+years?",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return 0.0
