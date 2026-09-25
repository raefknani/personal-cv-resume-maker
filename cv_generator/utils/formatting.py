"""
Centralised paragraph factory.

Provides make_paragraph() so all renderer code creates paragraphs from named
style tokens rather than scattering ParagraphStyle() calls everywhere.
"""
from __future__ import annotations

from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from ..styles.styles import TEXT_BODY, TEXT_DARK, TEXT_META


def _hex(color: str) -> HexColor:
    return HexColor(color)


def make_paragraph(
    text: str | None,
    *,
    font: str = "Helvetica",
    size: float = 9.0,
    leading: float = 11.0,
    color: str = TEXT_BODY,
    alignment: int = 0,
    left_indent: float = 0.0,
    space_after: float = 0.0,
    space_before: float = 0.0,
    style_name: str = "cv_auto",
) -> Paragraph:
    """Create a Paragraph with fully specified typography from token values."""
    value = "" if text is None else str(text)
    style = ParagraphStyle(
        style_name,
        fontName=font,
        fontSize=size,
        leading=leading,
        textColor=_hex(color),
        alignment=alignment,
        leftIndent=left_indent,
        spaceAfter=space_after,
        spaceBefore=space_before,
    )
    return Paragraph(value, style)


__all__ = ["make_paragraph"]
