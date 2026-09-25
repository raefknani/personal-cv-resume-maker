"""
Centralised ATS style tokens.

Three density profiles are defined:
  COMFORTABLE   – default; 9.0 pt body, generous spacing
  COMPACT       – 8.7 pt body, tighter spacing; tried if comfortable > 1 page
  ULTRA_COMPACT – 8.5 pt body, minimal safe spacing; last resort before 2-page

All spacing / font sizes in the builder must be sourced from the active
profile dict — no magic numbers are allowed in renderer code.
"""
from __future__ import annotations

from typing import Any

# Accent / separator colour — subtle navy; ATS-safe dark grey variant
ACCENT_NAVY = "#1E3A5F"
SEPARATOR_COLOR = "#2C3E50"   # dark charcoal — clearly visible, not garish
TEXT_DARK = "#111827"
TEXT_BODY = "#2A2A2A"
TEXT_META = "#333333"
LINK_COLOR = "#0B57D0"

# ---------------------------------------------------------------------------
# Profile definitions
# ---------------------------------------------------------------------------

_COMFORTABLE: dict[str, Any] = {
    # Page margins (points)
    "left_margin": 36,        # 0.50 in
    "right_margin": 36,
    "top_margin": 32,         # 0.44 in
    "bottom_margin": 32,

    # Fonts
    "name_size": 18,
    "title_size": 10,
    "contact_size": 8.8,
    "section_title_size": 10,
    "body_size": 9.0,
    "bullet_size": 9.0,
    "meta_size": 8.8,
    "job_title_size": 9.2,

    # Leading (line height)
    "name_leading": 20,
    "title_leading": 12,
    "contact_leading": 11,
    "section_title_leading": 12,
    "body_leading": 11.0,
    "bullet_leading": 11.0,

    # Spacers (points)
    "after_header": 4,
    "before_section": 5,
    "after_section_title": 3,
    "after_separator": 3,
    "after_profile": 3,
    "after_skill_row": 2,
    "after_exp_block": 5,
    "after_edu_block": 3,
    "after_cert_block": 3,
    "bullet_space_after": 2,

    # Separator
    "separator_thickness": 0.6,
    "separator_color": SEPARATOR_COLOR,
    "separator_space_before": 2,
    "separator_space_after": 3,

    # Bullet indent
    "bullet_left_indent": 10,
}

_COMPACT: dict[str, Any] = {
    **_COMFORTABLE,
    "body_size": 8.7,
    "bullet_size": 8.7,
    "meta_size": 8.5,
    "job_title_size": 9.0,
    "body_leading": 10.5,
    "bullet_leading": 10.5,
    "after_header": 3,
    "before_section": 4,
    "after_section_title": 2,
    "after_separator": 2,
    "after_profile": 2,
    "after_skill_row": 1,
    "after_exp_block": 4,
    "after_edu_block": 2,
    "after_cert_block": 2,
    "bullet_space_after": 1,
    "separator_space_before": 1,
    "separator_space_after": 2,
}

_ULTRA_COMPACT: dict[str, Any] = {
    **_COMPACT,
    # Margins: 28pt = 0.39 in — still print-safe
    "left_margin": 28,
    "right_margin": 28,
    "top_margin": 26,
    "bottom_margin": 26,
    "body_size": 8.5,
    "bullet_size": 8.5,
    "meta_size": 8.5,
    "job_title_size": 8.8,
    "body_leading": 10.0,
    "bullet_leading": 10.0,
    "after_header": 2,
    "before_section": 2,
    "after_section_title": 1,
    "after_separator": 1,
    "after_profile": 2,
    "after_skill_row": 1,
    "after_exp_block": 2,
    "after_edu_block": 2,
    "after_cert_block": 1,
    "bullet_space_after": 1,
    "separator_space_before": 1,
    "separator_space_after": 1,
}

DENSITY_PROFILES: dict[str, dict[str, Any]] = {
    "COMFORTABLE": _COMFORTABLE,
    "COMPACT": _COMPACT,
    "ULTRA_COMPACT": _ULTRA_COMPACT,
}

PROFILE_ORDER = ["COMFORTABLE", "COMPACT", "ULTRA_COMPACT"]


def get_profile(name: str) -> dict[str, Any]:
    """Return a copy of the named density profile."""
    if name not in DENSITY_PROFILES:
        raise ValueError(f"Unknown density profile: {name!r}. Choose from {list(DENSITY_PROFILES)}")
    return dict(DENSITY_PROFILES[name])


def build_styles() -> dict[str, Any]:
    """Return the COMFORTABLE profile (legacy compatibility shim)."""
    return get_profile("COMFORTABLE")


# Re-export colour constants for use in builder / helpers
__all__ = [
    "ACCENT_NAVY",
    "SEPARATOR_COLOR",
    "TEXT_DARK",
    "TEXT_BODY",
    "TEXT_META",
    "LINK_COLOR",
    "DENSITY_PROFILES",
    "PROFILE_ORDER",
    "get_profile",
    "build_styles",
]
