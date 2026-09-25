"""
CVBuilder — ATS-first single-column CV generator with density-profile
one-page optimisation.

Density fallback order:
  COMFORTABLE → COMPACT → ULTRA_COMPACT → accept 2 pages

All typography tokens come from the active density profile dict; there are
no magic numbers in rendering methods.
"""
from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from .config import CONFIG
from .styles.styles import (
    LINK_COLOR,
    PROFILE_ORDER,
    SEPARATOR_COLOR,
    TEXT_BODY,
    TEXT_DARK,
    TEXT_META,
    get_profile,
)
from .utils.helpers import format_date_range, render_section_title
from .utils.pdf_utils import count_pdf_pages
from .utils.validation import validate_cv_data
from .variants.general import apply_variant


# ---------------------------------------------------------------------------
# Internal paragraph factory
# ---------------------------------------------------------------------------

def _p(
    text: str | None,
    *,
    font: str = "Helvetica",
    size: float = 9.0,
    leading: float = 11.0,
    color: str = TEXT_BODY,
    alignment: int = 0,
    left_indent: float = 0.0,
    space_after: float = 0.0,
    space_before: float = 0.0,
    name: str = "cv_auto",
) -> Paragraph:
    """Internal paragraph factory — all sizes/colours come from profile tokens."""
    value = "" if text is None else str(text)
    style = ParagraphStyle(
        name,
        fontName=font,
        fontSize=size,
        leading=leading,
        textColor=HexColor(color),
        alignment=alignment,
        leftIndent=left_indent,
        spaceAfter=space_after,
        spaceBefore=space_before,
    )
    return Paragraph(value, style)


def _escape(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class CVBuilder:
    def __init__(
        self,
        data: dict[str, Any],
        config: dict[str, Any] | None = None,
        variant: dict[str, Any] | None = None,
    ):
        self.data = data
        self.config = config or CONFIG
        self.variant = variant
        # Legacy shim — kept so external code that accesses self.styles still works
        from .styles.styles import build_styles
        self.styles = build_styles()

    # ------------------------------------------------------------------
    # Variant / validation
    # ------------------------------------------------------------------

    def _with_variant(self) -> dict[str, Any]:
        if self.variant:
            return apply_variant(self.data, self.variant)
        return self.data

    # ------------------------------------------------------------------
    # Document setup
    # ------------------------------------------------------------------

    def _build_doc(self, output_path: Path, profile: dict[str, Any]) -> SimpleDocTemplate:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=profile["left_margin"],
            rightMargin=profile["right_margin"],
            topMargin=profile["top_margin"],
            bottomMargin=profile["bottom_margin"],
        )

    # ------------------------------------------------------------------
    # Section helpers
    # ------------------------------------------------------------------

    def _section_heading(self, title: str, profile: dict[str, Any]) -> list:
        """Return [Spacer, heading Paragraph, HRFlowable] for a section."""
        flowables: list = [Spacer(1, profile["before_section"])]
        flowables.extend(
            render_section_title(
                title,
                font_size=profile["section_title_size"],
                color=TEXT_DARK,
                separator_color=profile["separator_color"],
                separator_thickness=profile["separator_thickness"],
                separator_space_before=profile["separator_space_before"],
                separator_space_after=profile["separator_space_after"],
            )
        )
        flowables.append(Spacer(1, profile["after_section_title"]))
        return flowables

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _render_header(self, personal: dict[str, Any], profile: dict[str, Any]) -> list:
        name = personal.get("name", "")
        title = personal.get("title", "")
        location = personal.get("location", "")
        phone = personal.get("phone", "")
        email = personal.get("email", "")
        github = personal.get("github", "")
        linkedin = personal.get("linkedin", "")

        flowables: list = []

        # Candidate name — centred, bold, large
        flowables.append(
            _p(name,
               font="Helvetica-Bold",
               size=profile["name_size"],
               leading=profile["name_leading"],
               color=TEXT_DARK,
               alignment=1,
               name="cv_name")
        )

        # Professional title — centred, slightly smaller
        if title:
            flowables.append(
                _p(title,
                   font="Helvetica",
                   size=profile["title_size"],
                   leading=profile["title_leading"],
                   color=TEXT_DARK,
                   alignment=1,
                   space_after=2,
                   name="cv_title")
            )

        # Contact line 1: location | phone | email
        contact_parts: list[str] = []
        if location:
            contact_parts.append(location)
        if phone:
            contact_parts.append(phone)
        if email:
            contact_parts.append(f'<a href="mailto:{email}" color="{LINK_COLOR}">{email}</a>')
        if contact_parts:
            flowables.append(
                _p(" | ".join(contact_parts),
                   size=profile["contact_size"],
                   leading=profile["contact_leading"],
                   color=TEXT_DARK,
                   alignment=1,
                   space_after=1,
                   name="cv_contact1")
            )

        # Contact line 2: LinkedIn | GitHub (clickable)
        link_parts: list[str] = []
        if linkedin:
            link_parts.append(f'LinkedIn: <a href="{linkedin}" color="{LINK_COLOR}">{linkedin}</a>')
        if github:
            link_parts.append(f'GitHub: <a href="{github}" color="{LINK_COLOR}">{github}</a>')
        if link_parts:
            flowables.append(
                _p(" | ".join(link_parts),
                   size=profile["contact_size"],
                   leading=profile["contact_leading"],
                   color=TEXT_DARK,
                   alignment=1,
                   space_after=0,
                   name="cv_contact2")
            )

        # Separator after header
        flowables.append(Spacer(1, profile["after_header"]))
        return flowables

    # ------------------------------------------------------------------
    # Profile / Summary
    # ------------------------------------------------------------------

    def _render_profile(self, profile_text: str | None, profile: dict[str, Any]) -> list:
        if not profile_text:
            return []
        return [
            _p(str(profile_text),
               size=profile["body_size"],
               leading=profile["body_leading"],
               color=TEXT_BODY,
               space_after=profile["after_profile"],
               name="cv_profile"),
        ]

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    def _render_skills(self, skills: dict[str, list[str]], profile: dict[str, Any]) -> list:
        if not skills:
            return []

        mapping: dict[str, list[str]] = {
            "Programming Languages": [],
            "Frontend": [],
            "Backend": [],
            "Databases": [],
            "DevOps & Tools": [],
            "Systems & Other": [],
        }

        core = skills.get("core", [])
        familiar = skills.get("familiar", [])
        systems = skills.get("systems", [])
        seen: set[str] = set()

        def add_skill(category: str, value: Any) -> None:
            item = str(value).strip()
            key = item.lower()
            if item and key not in seen:
                mapping[category].append(item)
                seen.add(key)

        def classify(value: Any) -> str:
            lower = str(value).lower()
            if any(v in lower for v in ("javascript", "typescript", "java") if "spring" not in lower and "node" not in lower):
                # JavaScript and TypeScript are prog languages; Java only if not Spring/Node context
                if "spring" not in lower and "node" not in lower:
                    return "Programming Languages"
            if any(v in lower for v in ("python",)):
                return "Programming Languages"
            if any(v in lower for v in ("react", "next", "angular", "three", "tailwind", "framer", "css")):
                return "Frontend"
            if any(v in lower for v in ("fastapi", "django", "spring", "node", "api")):
                return "Backend"
            if any(v in lower for v in ("postgres", "sqlite", "supabase", "sqlalchemy")):
                return "Databases"
            if any(v in lower for v in ("git", "docker", "github", "linux", "agile", "scrum", "cloudinary", "ci", "cd", "actions")):
                return "DevOps & Tools"
            return "Systems & Other"

        # Override: explicitly assign well-known items first
        prog_lang_names = {"javascript", "python", "typescript", "java"}

        def classify_refined(value: Any) -> str:
            lower = str(value).lower()
            # Exact / prefix matches for programming languages
            for pl in prog_lang_names:
                if lower.startswith(pl):
                    return "Programming Languages"
            if any(v in lower for v in ("react", "next.js", "angular", "three.js", "tailwind", "framer", "css")):
                return "Frontend"
            if any(v in lower for v in ("fastapi", "django", "spring", "node.js", "node", "api")):
                return "Backend"
            if any(v in lower for v in ("postgres", "sqlite", "supabase", "sqlalchemy")):
                return "Databases"
            if any(v in lower for v in ("git", "docker", "github", "agile", "scrum", "cloudinary", "ci/cd", "actions")):
                return "DevOps & Tools"
            return "Systems & Other"

        for item in core:
            add_skill(classify_refined(item), item)
        for item in familiar:
            add_skill(classify_refined(item), item)
        for item in systems:
            add_skill("Systems & Other", item)

        lines: list = []
        for label, values in mapping.items():
            if not values:
                continue
            text = ", ".join(values)
            lines.append(
                _p(f"<b>{label}:</b> {text}",
                   size=profile["body_size"],
                   leading=profile["body_leading"],
                   color=TEXT_BODY,
                   space_after=profile["after_skill_row"],
                   name="cv_skill_row")
            )
        return lines

    # ------------------------------------------------------------------
    # Experience
    # ------------------------------------------------------------------

    def _render_experience(self, experiences: list[dict[str, Any]], profile: dict[str, Any]) -> list:
        if not experiences:
            return []

        flowables: list = []
        for exp in experiences:
            if not isinstance(exp, dict):
                continue

            position = exp.get("position", "")
            company = exp.get("company", "")
            location = exp.get("location", "")
            start_date = exp.get("start_date", "")
            end_date = exp.get("end_date", "")
            description = exp.get("description", []) or []

            # One-line header: Position — Company
            heading_text = f"{position} — {company}" if company else position
            meta_parts: list[str] = []
            date_str = format_date_range(start_date, end_date)
            if date_str:
                meta_parts.append(date_str)
            if location:
                meta_parts.append(location)
            meta_text = " | ".join(meta_parts)

            block: list = [
                _p(_escape(heading_text),
                   font="Helvetica-Bold",
                   size=profile["job_title_size"],
                   leading=profile["body_leading"],
                   color=TEXT_DARK,
                   space_after=1,
                   name="cv_job_title"),
            ]
            if meta_text:
                block.append(
                    _p(_escape(meta_text),
                       size=profile["meta_size"],
                       leading=profile["body_leading"],
                       color=TEXT_META,
                       space_after=2,
                       name="cv_job_meta")
                )

            bullet_style = ParagraphStyle(
                "cv_bullet",
                fontName="Helvetica",
                fontSize=profile["bullet_size"],
                leading=profile["bullet_leading"],
                textColor=HexColor(TEXT_BODY),
                leftIndent=profile["bullet_left_indent"] + 8,
                bulletIndent=profile["bullet_left_indent"],
                spaceAfter=profile["bullet_space_after"],
            )
            for bullet_text in description:
                block.append(Paragraph(f"<bullet>\u2022</bullet>{_escape(bullet_text)}", bullet_style))

            # Keep heading + first bullet together to avoid orphan headings
            if len(block) >= 2:
                flowables.append(KeepTogether(block[:2]))
                flowables.extend(block[2:])
            else:
                flowables.extend(block)

            flowables.append(Spacer(1, profile["after_exp_block"]))

        return flowables

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    def _render_projects(self, projects: list[dict[str, Any]], profile: dict[str, Any]) -> list:
        if not projects:
            return []

        flowables: list = []
        for project in projects:
            if not isinstance(project, dict):
                continue

            title = project.get("name", "")
            technologies = project.get("technologies", "")
            description = project.get("description", []) or []

            # One-line header: Project Name — Technologies
            heading_text = f"{title} — {technologies}" if technologies else title

            block: list = [
                _p(_escape(heading_text),
                   font="Helvetica-Bold",
                   size=profile["job_title_size"],
                   leading=profile["body_leading"],
                   color=TEXT_DARK,
                   space_after=2,
                   name="cv_project_header"),
            ]

            bullet_style = ParagraphStyle(
                "cv_bullet_proj",
                fontName="Helvetica",
                fontSize=profile["bullet_size"],
                leading=profile["bullet_leading"],
                textColor=HexColor(TEXT_BODY),
                leftIndent=profile["bullet_left_indent"] + 8,
                bulletIndent=profile["bullet_left_indent"],
                spaceAfter=profile["bullet_space_after"],
            )
            for bullet_text in description:
                block.append(Paragraph(f"<bullet>\u2022</bullet>{_escape(bullet_text)}", bullet_style))

            if len(block) >= 2:
                flowables.append(KeepTogether(block[:2]))
                flowables.extend(block[2:])
            else:
                flowables.extend(block)

            flowables.append(Spacer(1, profile["after_exp_block"]))

        return flowables

    # ------------------------------------------------------------------
    # Education
    # ------------------------------------------------------------------

    def _render_education(self, education: list[dict[str, Any]], profile: dict[str, Any]) -> list:
        if not education:
            return []

        flowables: list = []
        for item in education:
            if not isinstance(item, dict):
                continue
            degree = item.get("degree", "")
            institution = item.get("institution", "")
            start = item.get("start_date", "")
            end = item.get("end_date", "")
            date_str = format_date_range(start, end)

            # Compact one-line: Degree — Institution | Years
            line_parts: list[str] = []
            if degree:
                line_parts.append(f"<b>{_escape(degree)}</b>")
            if institution:
                line_parts.append(_escape(institution))
            heading = " — ".join(line_parts)
            if date_str:
                heading = f"{heading} | {_escape(date_str)}"

            block = [
                _p(heading,
                   size=profile["body_size"],
                   leading=profile["body_leading"],
                   color=TEXT_BODY,
                   space_after=profile["after_edu_block"],
                   name="cv_edu_entry"),
            ]
            flowables.append(KeepTogether(block))

        return flowables

    # ------------------------------------------------------------------
    # Certifications
    # ------------------------------------------------------------------

    def _render_certifications(self, certifications: list[dict[str, Any]], profile: dict[str, Any]) -> list:
        if not certifications:
            return []

        flowables: list = []
        for cert in certifications:
            if not isinstance(cert, dict):
                continue
            name = cert.get("name", "")
            institution = cert.get("institution", "")
            date_value = cert.get("date", "")

            # Single compact line
            parts: list[str] = []
            if name:
                parts.append(f"<b>{_escape(name)}</b>")
            if institution:
                parts.append(_escape(institution))
            if date_value:
                parts.append(_escape(date_value))
            line = " — ".join(parts)

            flowables.append(
                _p(line,
                   size=profile["body_size"],
                   leading=profile["body_leading"],
                   color=TEXT_BODY,
                   space_after=profile["after_cert_block"],
                   name="cv_cert_entry")
            )

        return flowables

    # ------------------------------------------------------------------
    # Languages
    # ------------------------------------------------------------------

    def _render_languages(self, languages: list[dict[str, str]], profile: dict[str, Any]) -> list:
        if not languages:
            return []

        parts: list[str] = []
        for lang in languages:
            if not isinstance(lang, dict):
                continue
            name = lang.get("name", "")
            level = lang.get("level", "")
            if name and level:
                parts.append(f"<b>{_escape(name)}:</b> {_escape(level)}")
        if not parts:
            return []

        return [
            _p(" | ".join(parts),
               size=profile["body_size"],
               leading=profile["body_leading"],
               color=TEXT_BODY,
               name="cv_languages")
        ]

    # ------------------------------------------------------------------
    # Story assembly
    # ------------------------------------------------------------------

    def _assemble_story(self, validated: dict[str, Any], profile: dict[str, Any]) -> list:
        story: list = []

        # Always render header
        story.extend(self._render_header(validated.get("personal", {}), profile))

        section_order = self.config.get(
            "section_order",
            ["profile", "skills", "experience", "projects", "education", "certifications", "languages"],
        )

        section_renderers = {
            "profile": (
                "include_profile",
                "PROFESSIONAL SUMMARY",
                lambda: self._render_profile(validated.get("profile"), profile),
            ),
            "skills": (
                "include_skills",
                "TECHNICAL SKILLS",
                lambda: self._render_skills(validated.get("skills", {}), profile),
            ),
            "experience": (
                "include_experience",
                "PROFESSIONAL EXPERIENCE",
                lambda: self._render_experience(validated.get("experience", []), profile),
            ),
            "projects": (
                "include_projects",
                "PROJECTS",
                lambda: self._render_projects(validated.get("projects", []), profile),
            ),
            "education": (
                "include_education",
                "EDUCATION",
                lambda: self._render_education(validated.get("education", []), profile),
            ),
            "certifications": (
                "include_certifications",
                "CERTIFICATIONS",
                lambda: self._render_certifications(validated.get("certifications", []), profile),
            ),
            "languages": (
                "include_languages",
                "LANGUAGES",
                lambda: self._render_languages(validated.get("languages", []), profile),
            ),
        }

        for section_name in section_order:
            if section_name not in section_renderers:
                continue
            toggle_key, heading, renderer = section_renderers[section_name]
            if not self.config.get(toggle_key, True):
                continue
            content = renderer()
            if content:
                story.extend(self._section_heading(heading, profile))
                story.extend(content)

        return story

    # ------------------------------------------------------------------
    # PDF generation with density-profile fallback
    # ------------------------------------------------------------------

    def _generate_to_path(self, story: list, output_path: Path, profile: dict[str, Any]) -> Path:
        """Write story to output_path using a temp-then-rename pattern."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix="cv_", suffix=".pdf", dir=str(output_path.parent), delete=False
        ) as tmp:
            temp_path = Path(tmp.name)
        try:
            doc = self._build_doc(temp_path, profile)
            doc.build(story)
            os.replace(temp_path, output_path)
            return output_path
        except Exception:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise

    def build(self, output_path: str | Path) -> str:
        output_file = Path(output_path)
        validated = self._with_variant()
        validate_cv_data(validated)

        prefer_single = self.config.get("prefer_single_page", True)
        min_font = float(self.config.get("minimum_body_font_size", 8.5))

        # Determine which profiles to try
        profiles_to_try = PROFILE_ORDER if prefer_single else ["COMFORTABLE"]

        last_exc: Exception | None = None
        result_path: Path | None = None

        for profile_name in profiles_to_try:
            profile = get_profile(profile_name)

            # Safety: never go below the configured minimum body font
            if profile["body_size"] < min_font:
                profile["body_size"] = min_font
                profile["bullet_size"] = min_font
                profile["meta_size"] = min_font

            story = self._assemble_story(validated, profile)

            try:
                result_path = self._generate_to_path(story, output_file, profile)
            except PermissionError:
                # Target file locked — write to a unique sibling path instead
                fallback = output_file.with_name(
                    f"{output_file.stem}_{uuid.uuid4().hex[:8]}{output_file.suffix}"
                )
                try:
                    result_path = self._generate_to_path(story, fallback, profile)
                except Exception as exc2:
                    raise ValueError(
                        f"Unable to generate PDF — output file is locked. "
                        f"Close {output_file.name} and try again."
                    ) from exc2
            except Exception as exc:
                raise ValueError(f"Unable to generate PDF: {exc}") from exc

            if not prefer_single:
                break

            pages = count_pdf_pages(result_path)
            if pages <= 1 or pages == 0:
                # 0 means pypdf unavailable — accept whatever was generated
                print(f"[CVBuilder] Profile={profile_name}, pages={pages} -> accepted")
                break
            print(f"[CVBuilder] Profile={profile_name}, pages={pages} -> trying next density profile")

        return str(result_path)
