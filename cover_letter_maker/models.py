from __future__ import annotations

from copy import deepcopy
from typing import Any


def default_cover_letter_data() -> dict[str, Any]:
    return {
        "personal": {
            "full_name": "",
            "professional_title": "",
            "address": "",
            "city": "",
            "country": "",
            "phone": "",
            "email": "",
            "linkedin": "",
            "github": "",
        },
        "application": {
            "job_title": "",
            "company_name": "",
            "company_address": "",
            "hiring_manager_name": "",
            "application_date": "",
            "reference": "",
        },
        "content": {
            "subject": "",
            "salutation": "Dear Hiring Manager,",
            "opening": "",
            "body_paragraphs": [],
            "closing": "Thank you for considering my application.",
            "typed_name": "",
        },
        "source_cv": {"profile": "", "skills": [], "experience": [], "education": []},
        "signature": {
            "enabled": False,
            "signature_id": None,
            "alignment": "left",
            "width_mm": 38,
            "vertical_spacing_mm": 2,
        },
        "template": {"name": "classic", "font_family": "Helvetica"},
    }


def merge_cover_letter_data(data: dict[str, Any] | None) -> dict[str, Any]:
    result = default_cover_letter_data()
    if not isinstance(data, dict):
        return result
    for section, values in data.items():
        if isinstance(values, dict) and isinstance(result.get(section), dict):
            result[section].update(values)
        else:
            result[section] = deepcopy(values)
    return result