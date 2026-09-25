"""
Shared rendering helpers for the CV generator.

All helpers are ATS-safe: they emit standard Platypus flowables with no
graphical elements that could confuse ATS text-extraction.
"""
from __future__ import annotations

from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import HRFlowable, Paragraph, Spacer, Table, TableStyle

from ..styles.styles import (
    SEPARATOR_COLOR,
    TEXT_BODY,
    TEXT_DARK,
    TEXT_META,
    ACCENT_NAVY,
)

DEFAULT_STYLE = {
    "body_text": colors.black,
    "muted_text": colors.HexColor("#4A5568"),
    "accent_cyan": colors.HexColor("#1D7FB5"),
    "primary_dark": colors.HexColor("#1F2A37"),
    "divider_line": colors.HexColor(SEPARATOR_COLOR),
}


def safe_paragraph(text: str | None, style: ParagraphStyle, *, bullet: bool = False) -> Paragraph:
    """Create a paragraph without crashing on empty or None input."""
    value = "" if text is None else str(text).strip()
    if bullet and value:
        value = f"• {value}"
    return Paragraph(value, style)


def render_section_title(
    title: str | None,
    *,
    font_size: float = 10.0,
    color: str = TEXT_DARK,
    separator_color: str = SEPARATOR_COLOR,
    separator_thickness: float = 0.6,
    separator_space_before: float = 2,
    separator_space_after: float = 3,
) -> list:
    """Render an ATS-friendly section heading followed by a visible HR separator.

    Returns a list of flowables: [Paragraph(title), HRFlowable(separator)]
    so that sections are visually distinct without any graphical objects that
    break ATS parsing.
    """
    if not title or not str(title).strip():
        return []

    style = ParagraphStyle(
        "cv_section_title",
        fontName="Helvetica-Bold",
        fontSize=font_size,
        textColor=HexColor(color),
        leading=font_size + 2,
        spaceAfter=0,
        leftIndent=0,
    )
    heading = Paragraph(str(title).upper(), style)
    separator = HRFlowable(
        width="100%",
        color=HexColor(separator_color),
        thickness=separator_thickness,
        spaceBefore=separator_space_before,
        spaceAfter=separator_space_after,
    )
    return [heading, separator]


def render_bullet(
    text: str | None,
    *,
    style: ParagraphStyle | None = None,
    bullet_char: str = "\u2022",
) -> Paragraph:
    """Render a bullet list item in a consistent compact format."""
    value = "" if text is None else str(text).strip()
    if not value:
        return Paragraph("", style or ParagraphStyle("empty_bullet", fontName="Helvetica", fontSize=9, leading=11))
    body = f"{bullet_char} {value}"
    if style is None:
        style = ParagraphStyle("cv_bullet", fontName="Helvetica", fontSize=9, leading=11, leftIndent=10)
    return Paragraph(body, style)


def render_bullet_list(
    items: Iterable[str | None],
    *,
    style: ParagraphStyle | None = None,
    bullet_char: str = "\u2022",
) -> list:
    """Render a list of bullet items as flowables."""
    flowables: list = []
    for item in items or []:
        text = "" if item is None else str(item).strip()
        if text:
            flowables.append(render_bullet(text, style=style, bullet_char=bullet_char))
    return flowables


def render_right_aligned_date(
    date_text: str | None,
    *,
    font_size: float = 8.5,
    text_color: str = TEXT_META,
) -> Paragraph:
    """Place date text right-aligned in a row."""
    value = "" if date_text is None else str(date_text).strip()
    style = ParagraphStyle(
        "cv_date",
        fontName="Helvetica",
        fontSize=font_size,
        textColor=HexColor(text_color),
        alignment=2,
        leading=font_size + 2,
    )
    return Paragraph(value, style)


def render_company_location(
    company: str | None,
    location: str | None,
    *,
    accent_color: str = ACCENT_NAVY,
) -> Paragraph:
    """Render the company and location line."""
    company_value = "" if company is None else str(company).strip()
    location_value = "" if location is None else str(location).strip()
    if company_value and location_value:
        text = f"<b>{company_value}</b> — {location_value}"
    elif company_value:
        text = f"<b>{company_value}</b>"
    elif location_value:
        text = location_value
    else:
        text = ""
    style = ParagraphStyle(
        "cv_company_location",
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=HexColor(TEXT_DARK),
    )
    return Paragraph(text, style)


def render_project_header(
    project_name: str | None,
    technologies: str | None,
    *,
    accent_color: str = ACCENT_NAVY,
) -> Table:
    """Create a project title/technologies row as a simple table."""
    name = "" if project_name is None else str(project_name).strip()
    tech = "" if technologies is None else str(technologies).strip()
    table = Table(
        [[
            Paragraph(name, ParagraphStyle("cv_project_name", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=HexColor(TEXT_DARK))),
            Paragraph(tech, ParagraphStyle("cv_project_tech", fontName="Helvetica", fontSize=8.5, leading=10, textColor=HexColor(accent_color), alignment=2)),
        ]],
        colWidths=[None, 160],
    )
    table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return table


def render_link(
    text: str,
    url: str | None,
    *,
    color: str = ACCENT_NAVY,
    underline: bool = False,
) -> Paragraph:
    """Render a clickable hyperlink."""
    if not url:
        return Paragraph(str(text), ParagraphStyle("cv_link", fontName="Helvetica", fontSize=9, textColor=HexColor(color), leading=11))
    display = str(text).strip() or url
    style = ParagraphStyle("cv_link", fontName="Helvetica", fontSize=9, textColor=HexColor(color), leading=11)
    return Paragraph(f'<a href="{url}" color="{color}">{display}</a>', style)


def render_separator(
    width: Any = "100%",
    color: str = SEPARATOR_COLOR,
    thickness: float = 0.6,
    space_before: float = 2,
    space_after: float = 3,
) -> HRFlowable:
    """Render a clearly visible but professional horizontal separator line."""
    return HRFlowable(
        width=width,
        color=HexColor(color),
        thickness=thickness,
        spaceBefore=space_before,
        spaceAfter=space_after,
    )


def format_date_range(start_date: str | None, end_date: str | None) -> str:
    """Format a date range consistently for display."""
    if start_date and end_date:
        if start_date == end_date:
            return str(start_date)
        return f"{start_date} – {end_date}"
    if start_date:
        return str(start_date)
    if end_date:
        return str(end_date)
    return ""


__all__ = [
    "safe_paragraph",
    "render_section_title",
    "render_bullet",
    "render_bullet_list",
    "render_right_aligned_date",
    "render_company_location",
    "render_project_header",
    "render_link",
    "render_separator",
    "format_date_range",
]
