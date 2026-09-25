from __future__ import annotations

from copy import deepcopy
from typing import Any


def apply_variant(base_data: dict[str, Any], variant: dict[str, Any] | None) -> dict[str, Any]:
    """Apply a variant to a deep-copied CV dataset without mutating the source."""
    if variant is None:
        return deepcopy(base_data)

    data = deepcopy(base_data)
    personal = data.setdefault("personal", {})

    if "title" in variant and variant["title"]:
        personal["title"] = str(variant["title"])
    if "profile" in variant and variant["profile"] is not None:
        data["profile"] = variant["profile"]
    if "skills" in variant and variant["skills"] is not None:
        data["skills"] = variant["skills"]
    if "experience" in variant and variant["experience"] is not None:
        data["experience"] = variant["experience"]
    if "projects" in variant and variant["projects"] is not None:
        data["projects"] = variant["projects"]
    if "education" in variant and variant["education"] is not None:
        data["education"] = variant["education"]
    if "certifications" in variant and variant["certifications"] is not None:
        data["certifications"] = variant["certifications"]
    if "languages" in variant and variant["languages"] is not None:
        data["languages"] = variant["languages"]
    if "section_order" in variant and variant["section_order"]:
        data["section_order"] = list(variant["section_order"])

    return data
