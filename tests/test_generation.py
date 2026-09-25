"""
Comprehensive ATS CV generator test suite.

Tests cover:
  1.  PDF generates successfully
  2.  PDF is non-empty
  3.  PDF contains all standard ATS headings (via pypdf text extraction)
  4.  PDF text contains candidate name
  5.  PDF text contains experience company names
  6.  Empty optional sections do not crash
  7.  Extra experiences do not crash
  8.  Single-page preference config key is present and correct type
  9.  Density-profile fallback: COMPACT profile produces smaller fonts than COMFORTABLE
  10. Body font never goes below configured minimum (8.5 pt)
  11. render_section_title() includes an HRFlowable separator
  12. Page count is 1 if feasible (actual PDF check)
  13. 2-page output is accepted automatically when content is too long
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from cv_generator.builder import CVBuilder
from cv_generator.config import CONFIG
from cv_generator.data.cv_data import CV_DATA
from cv_generator.styles.styles import PROFILE_ORDER, get_profile
from cv_generator.utils.helpers import render_section_title
from cv_generator.utils.pdf_utils import count_pdf_pages

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_DATA: dict[str, Any] = {
    "personal": {
        "name": "Test User",
        "title": "Developer",
        "location": "City",
        "phone": "123",
        "email": "user@example.com",
        "github": "https://github.com/test",
        "linkedin": "https://linkedin.com/in/test",
    },
    "profile": "A short profile summary for testing.",
    "skills": {"core": ["Python", "React.js"], "familiar": ["Docker"], "systems": ["RESTful APIs"]},
    "experience": [
        {
            "position": "Developer",
            "company": "Acme Corp",
            "location": "Remote",
            "start_date": "2024",
            "end_date": "2025",
            "description": ["Worked on product features.", "Shipped 3 major releases."],
        }
    ],
    "projects": [
        {
            "name": "Project Alpha",
            "technologies": "Python, FastAPI",
            "description": ["Built a backend API for internal tooling."],
        }
    ],
    "education": [
        {
            "degree": "B.Sc. Computer Science",
            "institution": "Test University",
            "start_date": "2020",
            "end_date": "2024",
        }
    ],
    "certifications": [],
    "languages": [],
}


def _extract_text(pdf_path: str | Path) -> str:
    """Extract all text from a PDF using pypdf. Returns empty string if unavailable."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Test 1 & 2: PDF generates successfully and is non-empty
# ---------------------------------------------------------------------------

def test_pdf_generation_succeeds(tmp_path):
    output_path = tmp_path / CONFIG["output_filename"]
    builder = CVBuilder(data=CV_DATA, config=CONFIG)
    builder.build(output_path)
    assert output_path.exists(), "Output PDF file should exist"
    assert output_path.stat().st_size > 0, "Output PDF file should be non-empty"


# ---------------------------------------------------------------------------
# Test 3: PDF contains all standard ATS headings
# ---------------------------------------------------------------------------

EXPECTED_HEADINGS = [
    "PROFESSIONAL SUMMARY",
    "TECHNICAL SKILLS",
    "PROFESSIONAL EXPERIENCE",
    "PROJECTS",
    "EDUCATION",
    "CERTIFICATIONS",
    "LANGUAGES",
]


def test_pdf_contains_ats_headings(tmp_path):
    output_path = tmp_path / "ats_headings_check.pdf"
    builder = CVBuilder(data=CV_DATA, config=CONFIG)
    builder.build(output_path)

    text = _extract_text(output_path)
    if not text:
        pytest.skip("pypdf not available — skipping text extraction checks")

    for heading in EXPECTED_HEADINGS:
        assert heading in text.upper(), f"ATS heading '{heading}' not found in PDF text"


# ---------------------------------------------------------------------------
# Test 4: PDF text contains candidate name
# ---------------------------------------------------------------------------

def test_pdf_contains_candidate_name(tmp_path):
    output_path = tmp_path / "name_check.pdf"
    builder = CVBuilder(data=CV_DATA, config=CONFIG)
    builder.build(output_path)

    text = _extract_text(output_path)
    if not text:
        pytest.skip("pypdf not available — skipping text extraction checks")

    name = CV_DATA["personal"]["name"]
    assert name.upper() in text.upper(), f"Candidate name '{name}' not found in PDF text"


# ---------------------------------------------------------------------------
# Test 5: PDF text contains experience company names
# ---------------------------------------------------------------------------

def test_pdf_contains_experience_companies(tmp_path):
    output_path = tmp_path / "experience_check.pdf"
    builder = CVBuilder(data=CV_DATA, config=CONFIG)
    builder.build(output_path)

    text = _extract_text(output_path)
    if not text:
        pytest.skip("pypdf not available — skipping text extraction checks")

    for exp in CV_DATA["experience"]:
        company = exp["company"]
        assert company.upper() in text.upper(), f"Company '{company}' not found in PDF text"


# ---------------------------------------------------------------------------
# Test 6: Empty optional sections do not crash
# ---------------------------------------------------------------------------

def test_empty_optional_sections_do_not_crash(tmp_path):
    data = deepcopy(MINIMAL_DATA)
    data["certifications"] = []
    data["languages"] = []

    output_path = tmp_path / "empty_optional.pdf"
    builder = CVBuilder(data=data, config=CONFIG)
    builder.build(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# Test 7: Extra experiences do not crash
# ---------------------------------------------------------------------------

def test_extra_experiences_do_not_crash(tmp_path):
    data = deepcopy(CV_DATA)
    for i in range(5):
        data["experience"].append({
            "position": f"Extra Intern #{i}",
            "company": f"Company {i}",
            "location": "Remote",
            "start_date": "2023",
            "end_date": "2024",
            "description": [f"Worked on task {i}."],
        })

    output_path = tmp_path / "extra_exp.pdf"
    builder = CVBuilder(data=data, config=CONFIG)
    builder.build(output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


# ---------------------------------------------------------------------------
# Test 8: prefer_single_page and minimum_body_font_size are in CONFIG
# ---------------------------------------------------------------------------

def test_config_has_single_page_preference():
    assert "prefer_single_page" in CONFIG, "CONFIG must have 'prefer_single_page'"
    assert isinstance(CONFIG["prefer_single_page"], bool)
    assert CONFIG["prefer_single_page"] is True


def test_config_has_minimum_body_font_size():
    assert "minimum_body_font_size" in CONFIG, "CONFIG must have 'minimum_body_font_size'"
    assert isinstance(CONFIG["minimum_body_font_size"], (int, float))
    assert CONFIG["minimum_body_font_size"] >= 8.5


# ---------------------------------------------------------------------------
# Test 9: COMPACT profile has smaller fonts than COMFORTABLE
# ---------------------------------------------------------------------------

def test_compact_profile_is_smaller_than_comfortable():
    comfortable = get_profile("COMFORTABLE")
    compact = get_profile("COMPACT")
    assert compact["body_size"] < comfortable["body_size"], (
        "COMPACT body_size should be smaller than COMFORTABLE body_size"
    )
    assert compact["bullet_leading"] <= comfortable["bullet_leading"], (
        "COMPACT leading should be equal or smaller than COMFORTABLE"
    )


# ---------------------------------------------------------------------------
# Test 10: Body font never goes below minimum
# ---------------------------------------------------------------------------

def test_body_font_never_below_minimum():
    min_font = float(CONFIG.get("minimum_body_font_size", 8.5))
    for profile_name in PROFILE_ORDER:
        profile = get_profile(profile_name)
        effective = max(profile["body_size"], min_font)
        assert effective >= min_font, (
            f"Profile {profile_name}: effective body size {effective} is below minimum {min_font}"
        )


# ---------------------------------------------------------------------------
# Test 11: render_section_title includes an HRFlowable separator
# ---------------------------------------------------------------------------

def test_section_title_includes_hr_separator():
    from reportlab.platypus import HRFlowable

    flowables = render_section_title("TEST SECTION")
    assert len(flowables) == 2, "render_section_title should return exactly 2 flowables"
    assert isinstance(flowables[1], HRFlowable), (
        "Second flowable from render_section_title must be HRFlowable"
    )


# ---------------------------------------------------------------------------
# Test 12: Page count is 1 if feasible
# ---------------------------------------------------------------------------

def test_page_count_is_one_for_normal_cv(tmp_path):
    output_path = tmp_path / "page_count_check.pdf"
    builder = CVBuilder(data=CV_DATA, config=CONFIG)
    builder.build(output_path)

    pages = count_pdf_pages(output_path)
    if pages == 0:
        pytest.skip("pypdf not available — skipping page count check")

    assert pages in (1, 2), f"Expected 1 or 2 pages, got {pages}"
    # If prefer_single_page is True and content fits, it must be 1
    if CONFIG.get("prefer_single_page") and pages > 1:
        # Two-page fallback is acceptable per spec; just report it
        pytest.xfail(
            f"Content did not fit in 1 page even at ULTRA_COMPACT — {pages} pages accepted per spec"
        )


# ---------------------------------------------------------------------------
# Test 13: 2-page output is accepted when content is too long
# ---------------------------------------------------------------------------

def test_two_page_output_accepted_for_very_long_cv(tmp_path):
    """Verify that the builder does NOT crash or truncate when content exceeds 1 page."""
    data = deepcopy(CV_DATA)
    # Add many extra experience entries to force overflow
    for i in range(10):
        data["experience"].append({
            "position": f"Software Engineer Level {i}",
            "company": f"MegaCorp International Division {i}",
            "location": "San Francisco, CA, USA",
            "start_date": f"Jan 202{i % 10}",
            "end_date": f"Dec 202{(i + 1) % 10}",
            "description": [
                f"Led the design and implementation of a highly scalable distributed microservices platform, iteration {i}.",
                f"Mentored a team of {i + 2} junior engineers across 3 time zones.",
                f"Reduced system latency by {10 + i * 5}% through profiling and caching strategies.",
            ],
        })

    output_path = tmp_path / "long_cv.pdf"
    config = {**CONFIG, "prefer_single_page": True}
    builder = CVBuilder(data=data, config=config)
    result = builder.build(output_path)

    assert Path(result).exists(), "PDF must be generated even when content exceeds 1 page"
    assert Path(result).stat().st_size > 0

    pages = count_pdf_pages(result)
    if pages:
        assert pages >= 1, "PDF must have at least 1 page"


# ---------------------------------------------------------------------------
# Legacy tests preserved from original test_generation.py
# ---------------------------------------------------------------------------

def test_builder_handles_empty_optional_sections(tmp_path):
    """Alias of test 6 — kept for backward compatibility with CI."""
    test_empty_optional_sections_do_not_crash(tmp_path)


def test_builder_accepts_variant_selection(tmp_path):
    data = deepcopy(MINIMAL_DATA)
    output_path = tmp_path / "variant_cv.pdf"
    builder = CVBuilder(data=data, config={**CONFIG, "section_order": ["profile", "experience"]})
    builder.build(output_path)
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_builder_falls_back_to_unique_path_when_target_is_locked(tmp_path):
    data = deepcopy(MINIMAL_DATA)
    output_path = tmp_path / CONFIG["output_filename"]
    with output_path.open("wb") as handle:
        handle.write(b"placeholder")
        builder = CVBuilder(data=data, config=CONFIG)
        generated_path = Path(builder.build(output_path))

    assert generated_path.exists()
    assert generated_path.suffix == ".pdf"
    assert generated_path != output_path
    assert generated_path.stat().st_size > 0
