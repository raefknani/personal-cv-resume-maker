from .styles import (
    build_styles,
    get_profile,
    DENSITY_PROFILES,
    PROFILE_ORDER,
    ACCENT_NAVY,
    SEPARATOR_COLOR,
    TEXT_DARK,
    TEXT_BODY,
    TEXT_META,
    LINK_COLOR,
)

# Legacy shim: STYLES is no longer a flat dict; export the COMFORTABLE profile for
# any code that may still reference cv_generator.styles.STYLES
from .styles import get_profile as _gp
STYLES = _gp("COMFORTABLE")

__all__ = [
    "build_styles",
    "get_profile",
    "DENSITY_PROFILES",
    "PROFILE_ORDER",
    "ACCENT_NAVY",
    "SEPARATOR_COLOR",
    "TEXT_DARK",
    "TEXT_BODY",
    "TEXT_META",
    "LINK_COLOR",
    "STYLES",
]
