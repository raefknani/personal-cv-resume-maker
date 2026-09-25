from copy import deepcopy

import pytest

from cv_generator.config import CONFIG
from cv_generator.data.cv_data import CV_DATA
from cv_generator.variants.general import apply_variant
from cv_generator.validation import validate_cv_data


def test_validation_passes_for_normal_cv_data():
    validate_cv_data(CV_DATA)


def test_validation_fails_when_name_missing():
    bad_data = deepcopy(CV_DATA)
    bad_data["personal"].pop("name")

    with pytest.raises(ValueError, match="name"):
        validate_cv_data(bad_data)


def test_empty_optional_section_does_not_crash():
    base = deepcopy(CV_DATA)
    base["certifications"] = []
    base["languages"] = []

    validate_cv_data(base)


def test_project_list_can_contain_additional_entries():
    extended = deepcopy(CV_DATA)
    extended["projects"].append({
        "name": "Additional Project",
        "technologies": "Python, FastAPI",
        "description": ["Built an API for internal tooling."],
    })

    validate_cv_data(extended)


def test_experience_list_can_contain_additional_entries():
    extended = deepcopy(CV_DATA)
    extended["experience"].append({
        "position": "Software Engineer Intern",
        "company": "Local Startup",
        "location": "Tunisia",
        "start_date": "Sep 2025",
        "end_date": "Dec 2025",
        "description": ["Built a prototype and shipped features."],
    })

    validate_cv_data(extended)


def test_variant_application_does_not_mutate_base_data():
    variant = {
        "title": "Software Engineer",
        "section_order": ["profile", "experience"],
    }

    original = deepcopy(CV_DATA)
    result = apply_variant(CV_DATA, variant)

    assert result["personal"]["title"] == "Software Engineer"
    assert CV_DATA["personal"]["title"] == original["personal"]["title"]
    assert result["section_order"] == ["profile", "experience"]
    assert "projects" in CV_DATA


def test_config_has_expected_sections():
    assert CONFIG["output_filename"] == "CV_Raef_Knani_ATS.pdf"
    assert "profile" in CONFIG["section_order"]
    assert "experience" in CONFIG["section_order"]
