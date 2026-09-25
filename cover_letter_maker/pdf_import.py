from __future__ import annotations

import io
import re
from typing import Any

from .models import default_cover_letter_data


def validate_pdf_bytes(content: bytes, filename: str = "") -> None:
    if not content.startswith(b"%PDF-"):
        raise ValueError("The uploaded file is not a valid PDF")
    if len(content) > 10 * 1024 * 1024:
        raise ValueError("PDF must be smaller than 10 MB")
    if filename and not filename.lower().endswith(".pdf"):
        raise ValueError("Please upload a PDF file")


def extract_cover_letter(content: bytes) -> dict[str, Any]:
    validate_pdf_bytes(content)
    try:
        from pypdf import PdfReader

        text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages)
    except Exception as exc:
        raise ValueError(f"Could not read PDF: {exc}") from exc
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        raise ValueError("This PDF has no selectable text")

    data = default_cover_letter_data()
    personal = data["personal"]
    application = data["application"]
    content_data = data["content"]
    personal["full_name"] = lines[0]
    if len(lines) > 1 and not re.search(r"@|\d{3,}|\b(?:dear|subject|re:|sincerely)\b", lines[1], re.I):
        personal["address"] = lines[1]
    emails = re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)
    phones = re.findall(r"(?:\+?\d[\d ()-]{6,}\d)", text)
    personal["email"] = emails[0] if emails else ""
    personal["phone"] = phones[0].strip() if phones else ""

    subject_index = next((i for i, line in enumerate(lines) if re.match(r"(?:subject|re)\s*:", line, re.I)), None)
    if subject_index is not None:
        content_data["subject"] = re.sub(r"^(?:subject|re)\s*:\s*", "", lines[subject_index], flags=re.I)
    date_match = next((line for line in lines if re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b", line)), "")
    application["application_date"] = date_match

    salutation_index = next((i for i, line in enumerate(lines) if re.match(r"dear\b", line, re.I)), None)
    closing_index = next((i for i, line in enumerate(lines) if re.match(r"(?:sincerely|kind regards|best regards|yours faithfully)", line, re.I)), None)
    if salutation_index is not None:
        content_data["salutation"] = lines[salutation_index]
        start = salutation_index + 1
    else:
        start = 0
    end = closing_index if closing_index is not None else len(lines)
    body = [line for line in lines[start:end] if line != content_data["subject"] and line != date_match]
    if body:
        content_data["opening"] = body[0]
        content_data["body_paragraphs"] = body[1:]
    if closing_index is not None:
        content_data["closing"] = lines[closing_index]
        if closing_index + 1 < len(lines):
            content_data["typed_name"] = lines[closing_index + 1]
    confidence = min(0.95, 0.35 + sum(bool(value) for value in (personal["email"], personal["phone"], content_data["subject"], content_data["opening"])) * 0.15)
    return {"data": data, "confidence": round(confidence, 2), "warnings": ["Please review imported fields before generating."]}