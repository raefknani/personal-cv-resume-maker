from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

from .models import merge_cover_letter_data


class CoverLetterRenderer:
    def render(self, data: dict[str, Any], signature_path: str | Path | None = None, output_path: str | Path = "cover_letter.pdf") -> str:
        data = merge_cover_letter_data(data)
        personal, application, content = data["personal"], data["application"], data["content"]
        template = data["template"].get("name", "classic")
        margins = {"classic": 22, "modern": 18, "minimal": 25, "ats": 20}.get(template, 22)
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=margins * mm, rightMargin=margins * mm, topMargin=20 * mm, bottomMargin=20 * mm)
        styles = getSampleStyleSheet()
        body = ParagraphStyle("letter_body", parent=styles["BodyText"], fontName=data["template"].get("font_family", "Helvetica"), fontSize=10.5, leading=15, spaceAfter=9)
        small = ParagraphStyle("letter_small", parent=body, fontSize=9, leading=12)
        right = ParagraphStyle("letter_right", parent=small, alignment=TA_RIGHT)
        story = []
        name = html.escape(personal.get("full_name", ""))
        story.append(Paragraph(f"<b>{name}</b>", ParagraphStyle("letter_name", parent=body, fontSize=17, leading=21, alignment=TA_CENTER, spaceAfter=3)))
        contact = " | ".join(filter(None, [personal.get("address"), personal.get("city"), personal.get("country"), personal.get("phone"), personal.get("email")]))
        if contact:
            story.append(Paragraph(html.escape(contact), ParagraphStyle("letter_contact", parent=small, alignment=TA_CENTER, spaceAfter=18)))
        if application.get("application_date"):
            story.append(Paragraph(html.escape(application["application_date"]), right))
        recipient = "<br/>".join(filter(None, [application.get("hiring_manager_name"), application.get("company_name"), application.get("company_address")]))
        if recipient:
            story.append(Paragraph(html.escape(recipient), body))
        if content.get("subject"):
            story.append(Paragraph(f"<b>{html.escape(content['subject'])}</b>", body))
        for paragraph in filter(None, [content.get("salutation"), content.get("opening"), *content.get("body_paragraphs", [])]):
            story.append(Paragraph(html.escape(str(paragraph)).replace("\n", "<br/>"), body))
        if content.get("closing"):
            story.append(Paragraph(html.escape(content["closing"]), body))
        signature = data.get("signature", {})
        if signature.get("enabled") and signature_path and Path(signature_path).exists():
            story.append(Spacer(1, float(signature.get("vertical_spacing_mm", 2)) * mm))
            width = float(signature.get("width_mm", 38)) * mm
            image = Image(str(signature_path), width=width, height=width * 0.28)
            image.hAlign = {"left": "LEFT", "center": "CENTER", "right": "RIGHT"}.get(signature.get("alignment", "left"), "LEFT")
            story.append(image)
        if content.get("typed_name"):
            story.append(Paragraph(html.escape(content["typed_name"]), body))
        doc.build(story)
        return str(output)