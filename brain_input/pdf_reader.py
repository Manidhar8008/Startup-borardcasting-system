# -*- coding: utf-8 -*-
"""PDF Reader — Extracts text from founder research PDFs.

Supports single and multi-page PDF files.
Falls back gracefully when pdfplumber is not installed.

Usage:
    from brain_input.pdf_reader import read_pdf, read_all_pdfs
    text = read_pdf("path/to/research.pdf")
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("brain_input")

RESEARCH_DIR = Path(__file__).resolve().parent / "research"


def read_pdf(path: str | Path) -> str:
    """Extract text from a single PDF file.

    Args:
        path: Absolute or relative path to the PDF.

    Returns:
        Extracted text string. Empty string on failure.
    """
    path = Path(path)
    if not path.exists():
        logger.warning("PDF not found: %s", path)
        return ""

    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        full_text = "\n\n".join(text_parts)
        logger.info("Read PDF '%s': %d pages, %d chars", path.name, len(text_parts), len(full_text))
        return full_text

    except ImportError:
        logger.warning("pdfplumber not installed. Run: pip install pdfplumber")
        return ""
    except Exception as exc:
        logger.error("Failed to read PDF '%s': %s", path, exc)
        return ""


def read_all_pdfs(directory: Optional[str | Path] = None) -> List[Dict]:
    """Read all PDF files from the research directory.

    Args:
        directory: Override directory. Default: brain_input/research/

    Returns:
        List of dicts with 'filename', 'text', 'pages', 'chars'.
    """
    search_dir = Path(directory) if directory else RESEARCH_DIR
    if not search_dir.exists():
        search_dir.mkdir(parents=True, exist_ok=True)
        return []

    results = []
    for pdf_path in sorted(search_dir.glob("*.pdf")):
        text = read_pdf(pdf_path)
        if text:
            results.append({
                "filename": pdf_path.name,
                "path": str(pdf_path),
                "text": text,
                "chars": len(text),
            })
    logger.info("Read %d PDFs from %s", len(results), search_dir)
    return results


def latest_pdf(directory: Optional[str | Path] = None) -> Optional[Dict]:
    """Return the most recently modified PDF from the research directory."""
    search_dir = Path(directory) if directory else RESEARCH_DIR
    if not search_dir.exists():
        return None

    pdfs = sorted(search_dir.glob("*.pdf"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not pdfs:
        return None

    text = read_pdf(pdfs[0])
    return {
        "filename": pdfs[0].name,
        "path": str(pdfs[0]),
        "text": text,
        "chars": len(text),
    }


__all__ = ["read_pdf", "read_all_pdfs", "latest_pdf"]
