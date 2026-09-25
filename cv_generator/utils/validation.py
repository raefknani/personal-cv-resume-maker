import re
from copy import deepcopy
from typing import Any


_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_URL_RE = re.compile(r"^https?://[\w.-]+(?:\.[\w.-]+)+(?:[/?#][^\s]*)?$", re.IGNORECASE)


def validate_cv_data(cv_data: dict[str, Any]) -> None:
    """Validate the central CV data structure and raise helpful errors for missing data."""
    if not isinstance(cv_data, dict):
        raise ValueError("CV data must be a dictionary.")

    personal = cv_data.get("personal")
    if not isinstance(personal, dict) or not personal:
        raise ValueError("Missing required section: personal")

    name = personal.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Missing required field: personal.name")

    email = personal.get("email")
    if email is not None and (not isinstance(email, str) or not _EMAIL_RE.match(email.strip())):
        raise ValueError("personal.email is malformed")

    for field_name in ("github", "linkedin"):
        value = personal.get(field_name)
        if value is not None and (not isinstance(value, str) or not _URL_RE.match(value.strip())):
            raise ValueError(f"personal.{field_name} has an invalid URL")

    for section_name in ("experience", "projects", "education"):
        value = cv_data.get(section_name)
        if value is None:
            raise ValueError(f"Missing required section: {section_name}")
        if not isinstance(value, list):
            raise ValueError(f"{section_name} must be a list")

    for index, item in enumerate(cv_data.get("experience", []), start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Experience #{index} must be a dictionary")
        for field_name in ("position", "company"):
            if not item.get(field_name):
                raise ValueError(f"Experience #{index} is missing required field: {field_name}")
        if "description" not in item or not isinstance(item["description"], list) or not item["description"]:
            raise ValueError(f"Experience #{index} must include a non-empty description list")

    for index, item in enumerate(cv_data.get("projects", []), start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Project #{index} must be a dictionary")
        if not item.get("name"):
            raise ValueError(f"Project #{index} is missing required field: name")
        if "description" not in item or not isinstance(item["description"], list):
            raise ValueError(f"Project #{index} has invalid description type")

    for index, item in enumerate(cv_data.get("education", []), start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Education #{index} must be a dictionary")
        if not item.get("degree"):
            raise ValueError(f"Education #{index} is missing required field: degree")
        if not item.get("institution"):
            raise ValueError(f"Education #{index} is missing required field: institution")

    skills = cv_data.get("skills")
    if skills is not None:
        if not isinstance(skills, dict):
            raise ValueError("skills must be a dictionary")
        for key in ("core", "familiar", "systems"):
            if key in skills and skills[key] is not None and not isinstance(skills[key], list):
                raise ValueError(f"skills.{key} must be a list")

    optional_sections = ("certifications", "languages")
    for section_name in optional_sections:
        value = cv_data.get(section_name)
        if value is not None and not isinstance(value, list):
            raise ValueError(f"{section_name} must be a list when present")

    for section_name in ("experience", "projects", "education", "certifications", "languages"):
        if section_name in cv_data and cv_data[section_name] == {}:
            raise ValueError(f"{section_name} cannot be an empty dictionary")


def apply_variant_defaults(base_data: dict[str, Any], variant: dict[str, Any] | None) -> dict[str, Any]:
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
