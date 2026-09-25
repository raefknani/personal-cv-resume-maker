"""
PDF utility helpers — page-count detection and build wrapper.
"""
from __future__ import annotations

from pathlib import Path


def count_pdf_pages(path: str | Path) -> int:
    """Return the number of pages in a PDF file using pypdf.

    Falls back to returning 0 if pypdf is unavailable or the file cannot be
    read, so callers can handle this gracefully without crashing.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        # pypdf not installed — cannot count pages; treat as unknown (0)
        return 0

    try:
        reader = PdfReader(str(path))
        return len(reader.pages)
    except Exception:
        return 0


__all__ = ["count_pdf_pages"]
