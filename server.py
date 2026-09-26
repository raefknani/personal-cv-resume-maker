import json
import io
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel

from cv_generator.builder import CVBuilder
from cv_generator.config import CONFIG
from cv_generator.data.cv_data import CV_DATA
from cv_generator.validation import validate_cv_data
from cover_letter_maker.models import merge_cover_letter_data
from cover_letter_maker.pdf_import import extract_cover_letter
from cover_letter_maker.renderer import CoverLetterRenderer
from cover_letter_maker.signature import SignatureProcessor, TemporarySignatureStorage
from cover_letter_maker.template_generator import SignatureTemplateGenerator

app = FastAPI(title="CV Generator API")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://cv-resume-maker-frontend.vercel.app",
    FRONTEND_URL.rstrip("/"),
}

# Allow CORS for local development with Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(origin for origin in allowed_origins if origin),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_DIR = Path(__file__).resolve().parent
SERVERLESS = bool(os.getenv("VERCEL"))
RUNTIME_DATA_DIR = Path("/tmp/pdf-creator") if SERVERLESS else PROJECT_DIR
RUNTIME_DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = RUNTIME_DATA_DIR / "saved_data.json"
LIBRARY_FILE = RUNTIME_DATA_DIR / "cv_library.json"
GOOGLE_TOKEN_FILE = Path(os.getenv("GOOGLE_TOKEN_FILE", Path(__file__).resolve().parent / ".google-drive-token.json"))
GOOGLE_CLIENT_SECRET_FILE = Path(os.getenv("GOOGLE_CLIENT_SECRET_FILE", Path(__file__).resolve().parent / "credentials.json"))
GOOGLE_DRIVE_REDIRECT_URI = os.getenv("GOOGLE_DRIVE_REDIRECT_URI", "http://127.0.0.1:8000/api/google-drive/callback")
OUTPUT_DIR = (Path("/tmp/pdf-creator/output") if SERVERLESS else PROJECT_DIR / "cv_generator" / "output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMP_SIGNATURE_DIR = (Path("/tmp/pdf-creator/signatures") if SERVERLESS else PROJECT_DIR / "temp" / "signatures")
TEMP_SIGNATURE_DIR.mkdir(parents=True, exist_ok=True)
signature_processor = SignatureProcessor()
signature_storage = TemporarySignatureStorage(TEMP_SIGNATURE_DIR)
signature_assets: dict[str, dict[str, Any]] = {}
_google_oauth_flow = None

class CVDataModel(BaseModel):
    """Request envelope for the complete, nested CV data structure."""

    data: Dict[str, Any]


class LibraryItemModel(BaseModel):
    """A named CV snapshot saved for later editing."""

    name: str
    data: Dict[str, Any]


class CloudSaveModel(BaseModel):
    """A CV payload and optional Drive filename."""

    data: Dict[str, Any]
    name: str = "CV Studio - Current.json"


class CoverLetterModel(BaseModel):
    data: Dict[str, Any]


PDF_SECTIONS = {
    "PROFESSIONAL SUMMARY": "profile",
    "TECHNICAL SKILLS": "skills",
    "PROFESSIONAL EXPERIENCE": "experience",
    "PROJECTS": "projects",
    "EDUCATION": "education",
    "CERTIFICATIONS": "certifications",
    "LANGUAGES": "languages",
}


def load_cv_data() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    # Fallback to the original data
    return CV_DATA


def _validate_payload(data: dict) -> None:
    try:
        validate_cv_data(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _save_cv_data(data: dict) -> None:
    """Write saved data atomically so an interrupted request cannot corrupt it."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=DATA_FILE.parent,
        prefix=f"{DATA_FILE.stem}_",
        suffix=".tmp",
        delete=False,
    ) as temp_file:
        temp_path = Path(temp_file.name)
        json.dump(data, temp_file, indent=2, ensure_ascii=False)
        temp_file.write("\n")

    try:
        os.replace(temp_path, DATA_FILE)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _load_library() -> list[dict[str, Any]]:
    if not LIBRARY_FILE.exists():
        return []
    try:
        with LIBRARY_FILE.open("r", encoding="utf-8") as file:
            value = json.load(file)
        return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        return []


def _save_library(items: list[dict[str, Any]]) -> None:
    """Write the complete library atomically."""
    LIBRARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=LIBRARY_FILE.parent,
        prefix=f"{LIBRARY_FILE.stem}_",
        suffix=".tmp",
        delete=False,
    ) as temp_file:
        temp_path = Path(temp_file.name)
        json.dump(items, temp_file, indent=2, ensure_ascii=False)
        temp_file.write("\n")

    try:
        os.replace(temp_path, LIBRARY_FILE)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def _google_drive_service():
    """Build an authenticated Drive client, or return None when not configured."""
    global _google_oauth_flow
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
    except ImportError:
        return None

    if not GOOGLE_TOKEN_FILE.exists():
        return None
    credentials = Credentials.from_authorized_user_file(str(GOOGLE_TOKEN_FILE), ["https://www.googleapis.com/auth/drive.file"])
    if not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request

            credentials.refresh(Request())
            GOOGLE_TOKEN_FILE.write_text(credentials.to_json(), encoding="utf-8")
        else:
            return None
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def _require_google_drive():
    service = _google_drive_service()
    if service is None:
        raise HTTPException(status_code=503, detail="Google Drive is not connected. Configure credentials.json and connect Google Drive first.")
    return service


@app.get("/api/google-drive/status")
def google_drive_status():
    configured = GOOGLE_CLIENT_SECRET_FILE.exists()
    connected = _google_drive_service() is not None
    return {"configured": configured, "connected": connected}


@app.get("/api/google-drive/connect")
def google_drive_connect():
    global _google_oauth_flow
    if not GOOGLE_CLIENT_SECRET_FILE.exists():
        raise HTTPException(status_code=503, detail="Add a Google OAuth Web application credentials.json file to the project root first.")
    try:
        from google_auth_oauthlib.flow import Flow

        _google_oauth_flow = Flow.from_client_secrets_file(
            str(GOOGLE_CLIENT_SECRET_FILE),
            scopes=["https://www.googleapis.com/auth/drive.file"],
            redirect_uri=GOOGLE_DRIVE_REDIRECT_URI,
        )
        authorization_url, _ = _google_oauth_flow.authorization_url(
            access_type="offline", prompt="consent", include_granted_scopes="true"
        )
        return RedirectResponse(authorization_url)
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="Google Drive dependencies are not installed.") from exc


@app.get("/api/google-drive/callback")
def google_drive_callback(code: str):
    global _google_oauth_flow
    if _google_oauth_flow is None:
        raise HTTPException(status_code=400, detail="Google authorization expired. Please connect again.")
    try:
        _google_oauth_flow.fetch_token(code=code)
        GOOGLE_TOKEN_FILE.write_text(_google_oauth_flow.credentials.to_json(), encoding="utf-8")
        _google_oauth_flow = None
        return RedirectResponse(f"{FRONTEND_URL}/?google_drive=connected")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Google authorization failed: {exc}") from exc


def _drive_files(service):
    return service.files().list(
        spaces="appDataFolder",
        q="trashed = false",
        fields="files(id,name,modifiedTime,size)",
        orderBy="modifiedTime desc",
    ).execute().get("files", [])


@app.get("/api/google-drive/files")
def list_google_drive_files():
    service = _require_google_drive()
    return _drive_files(service)


@app.get("/api/google-drive/files/{file_id}")
def load_google_drive_file(file_id: str):
    service = _require_google_drive()
    try:
        from googleapiclient.http import MediaIoBaseDownload

        request = service.files().get_media(fileId=file_id)
        buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(buffer, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        payload = json.loads(buffer.getvalue().decode("utf-8"))
        _validate_payload(payload)
        return {"data": payload}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not load Google Drive file: {exc}") from exc


@app.post("/api/google-drive/files")
def save_google_drive_file(payload: CloudSaveModel):
    _validate_payload(payload.data)
    service = _require_google_drive()
    try:
        from googleapiclient.http import MediaIoBaseUpload

        name = payload.name.strip() or "CV Studio - Current.json"
        body = json.dumps(payload.data, indent=2, ensure_ascii=False).encode("utf-8")
        existing = next((file for file in _drive_files(service) if file["name"] == name), None)
        media = MediaIoBaseUpload(io.BytesIO(body), mimetype="application/json", resumable=False)
        if existing:
            result = service.files().update(fileId=existing["id"], media_body=media, fields="id,name,modifiedTime").execute()
        else:
            result = service.files().create(
                body={"name": name, "parents": ["appDataFolder"]},
                media_body=media,
                fields="id,name,modifiedTime",
            ).execute()
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not save to Google Drive: {exc}") from exc


def _clean_pdf_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.replace("\u2022", "").strip())


def _normalize_phone(value: str) -> str:
    """Normalize common phone formats damaged by PDF text extraction."""
    cleaned = re.sub(r"\s+", " ", value.strip())
    digits = re.sub(r"\D", "", cleaned)

    # PDFs can turn ``+216 (98) 980 066`` into ``216) 98 980 066``.
    # Tunisia numbers have eight digits after the country code.
    if len(digits) == 11 and digits.startswith("216"):
        return f"+216 {digits[3:5]} {digits[5:8]} {digits[8:]}"

    return re.sub(r"[()]", "", cleaned).strip()


def _split_dash_line(line: str) -> list[str]:
    return [part.strip() for part in re.split(r"\s+[—–-]\s+", line) if part.strip()]


def _parse_pdf_text(text: str) -> dict[str, Any]:
    """Parse the headings and common line formats produced by CV PDFs."""
    lines = [_clean_pdf_line(line) for line in text.splitlines()]
    lines = [line for line in lines if line]
    sections: dict[str, list[str]] = {key: [] for key in PDF_SECTIONS.values()}
    current: str | None = None
    header: list[str] = []

    for line in lines:
        section = PDF_SECTIONS.get(line.upper())
        if section:
            current = section
            continue
        if current is None:
            header.append(line)
        else:
            sections[current].append(line)

    name = header[0] if header else "Imported CV"
    title = header[1] if len(header) > 1 else ""
    personal = {"name": name, "title": title, "location": "", "phone": "", "email": "", "github": "", "linkedin": ""}

    for line in header[2:]:
        email = re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", line)
        phone = re.search(r"(?:\+?\d[\d ()-]{6,}\d)", line)
        if email:
            personal["email"] = email.group(0)
        if phone:
            personal["phone"] = _normalize_phone(phone.group(0))
        linkedin = re.search(r"https?://\S*linkedin\.com/\S*", line, re.IGNORECASE)
        github = re.search(r"https?://\S*github\.com/\S*", line, re.IGNORECASE)
        if linkedin:
            personal["linkedin"] = linkedin.group(0).rstrip(".,")
        if github:
            personal["github"] = github.group(0).rstrip(".,")
        if not personal["location"] and "|" in line:
            personal["location"] = line.split("|")[0].strip()

    skills = {"core": [], "familiar": [], "systems": []}
    skill_categories = {
        "PROGRAMMING LANGUAGES": "core",
        "FRONTEND": "core",
        "BACKEND": "core",
        "DATABASES": "core",
        "DEVOPS & TOOLS": "familiar",
        "SYSTEMS & OTHER": "systems",
    }
    for line in sections["skills"]:
        label, separator, values = line.partition(":")
        category = skill_categories.get(label.upper()) if separator else None
        if category:
            skills[category].extend(item.strip() for item in values.split(",") if item.strip())

    def parse_entries(lines: list[str], kind: str) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        for line in lines:
            if kind == "experience" and current and " | " in line and re.search(r"\d{4}", line):
                dates, _, location = line.partition(" | ")
                date_parts = re.split(r"\s+[–—-]\s+", dates)
                current["start_date"] = date_parts[0].strip()
                current["end_date"] = date_parts[1].strip() if len(date_parts) > 1 else ""
                current["location"] = location.strip()
                continue

            is_heading = bool(re.search(r"\s+[—–-]\s+", line))
            if current and not is_heading:
                if current:
                    current["description"].append(line)
                continue

            parts = _split_dash_line(line)
            if not parts:
                continue
            if current:
                entries.append(current)
            if kind == "experience":
                current = {"position": parts[0], "company": parts[1] if len(parts) > 1 else "", "location": "", "start_date": "", "end_date": "", "description": []}
            elif kind == "projects":
                current = {"name": parts[0], "technologies": parts[1] if len(parts) > 1 else "", "description": []}
        if current:
            entries.append(current)
        return entries

    experience = parse_entries(sections["experience"], "experience")

    projects = parse_entries(sections["projects"], "projects")
    education = []
    for line in sections["education"]:
        parts = _split_dash_line(line)
        if not parts:
            continue
        degree = parts[0]
        institution = parts[1] if len(parts) > 1 else ""
        dates = parts[2] if len(parts) > 2 else ""
        date_parts = re.split(r"\s+[–—-]\s+", dates)
        education.append({"degree": degree, "institution": institution, "start_date": date_parts[0] if date_parts else "", "end_date": date_parts[1] if len(date_parts) > 1 else ""})

    certifications = []
    for line in sections["certifications"]:
        parts = _split_dash_line(line)
        certifications.append({"name": parts[0], "institution": parts[1] if len(parts) > 1 else "", "date": parts[2] if len(parts) > 2 else ""})

    languages = []
    for line in sections["languages"]:
        for item in line.split("|"):
            name, separator, level = item.partition(":")
            if separator:
                languages.append({"name": name.strip(), "level": level.strip()})

    return {
        "personal": personal,
        "profile": " ".join(sections["profile"]),
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "education": education,
        "certifications": certifications,
        "languages": languages,
    }


@app.post("/api/import-pdf")
async def import_pdf(file: UploadFile = File(...)):
    """Extract editable CV fields from a text-based PDF upload."""
    filename_is_pdf = (file.filename or "").lower().endswith(".pdf")
    if file.content_type not in (None, "application/pdf", "application/octet-stream") and not filename_is_pdf:
        raise HTTPException(status_code=400, detail="Please upload a PDF file")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="PDF must be smaller than 10 MB")

    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {exc}") from exc

    if not text.strip():
        raise HTTPException(status_code=422, detail="This PDF has no selectable text. Scanned PDFs are not supported yet.")

    return {"data": _parse_pdf_text(text), "filename": file.filename or "uploaded.pdf"}


@app.get("/api/cover-letters/default")
def get_default_cover_letter():
    return merge_cover_letter_data(None)


@app.post("/api/cover-letters/import-pdf")
async def import_cover_letter_pdf(file: UploadFile = File(...)):
    content = await file.read()
    try:
        result = extract_cover_letter(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {**result, "filename": file.filename or "uploaded.pdf"}


async def _process_signature(file: UploadFile, mode: str):
    content = await file.read()
    try:
        result = signature_processor.process_template_scan(content) if mode == "template_scan" else signature_processor.process_upload(content)
        asset = signature_storage.save(result)
        signature_assets[asset["signature_id"]] = asset
        return {**{key: value for key, value in asset.items() if key != "path"}, "status": "success", "preview_url": f"/api/signatures/{asset['signature_id']}/preview"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/signatures/template")
def download_signature_template():
    from fastapi.responses import Response

    return Response(SignatureTemplateGenerator().generate_pdf(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=signature-template.pdf"})


@app.post("/api/signatures/upload")
async def upload_signature(file: UploadFile = File(...)):
    return await _process_signature(file, "direct_upload")


@app.post("/api/signatures/process-upload")
async def process_signature_upload(file: UploadFile = File(...)):
    return await _process_signature(file, "direct_upload")


@app.post("/api/signatures/process-template")
async def process_signature_template(file: UploadFile = File(...)):
    return await _process_signature(file, "template_scan")


@app.get("/api/signatures/{signature_id}/preview")
def preview_signature(signature_id: str):
    asset = signature_assets.get(signature_id)
    if not asset or not Path(asset["path"]).exists():
        raise HTTPException(status_code=404, detail="Signature asset not found or expired")
    return FileResponse(asset["path"], media_type="image/png", filename="signature-preview.png")


@app.delete("/api/signatures/{signature_id}")
def delete_signature(signature_id: str):
    asset = signature_assets.pop(signature_id, None)
    if not asset:
        raise HTTPException(status_code=404, detail="Signature asset not found")
    Path(asset["path"]).unlink(missing_ok=True)
    return {"status": "success"}


@app.post("/api/cover-letters/generate")
def generate_cover_letter(payload: CoverLetterModel):
    data = merge_cover_letter_data(payload.data)
    signature_id = data.get("signature", {}).get("signature_id")
    asset = signature_assets.get(signature_id) if signature_id else None
    output_path = OUTPUT_DIR / f"cover_letter_{uuid4().hex[:8]}.pdf"
    try:
        result = CoverLetterRenderer().render(data, asset["path"] if asset else None, output_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cover-letter generation failed: {exc}") from exc
    return FileResponse(result, filename="cover-letter.pdf", media_type="application/pdf")


@app.get("/api/cv")
def get_cv_data():
    return load_cv_data()


@app.post("/api/cv")
def save_cv_data(payload: CVDataModel):
    try:
        _validate_payload(payload.data)
        _save_cv_data(payload.data)
        return {"status": "success", "message": "CV data saved successfully."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/library")
def get_library():
    """Return saved CV snapshots, newest first."""
    return sorted(_load_library(), key=lambda item: item.get("created_at", ""), reverse=True)


@app.post("/api/library")
def save_to_library(payload: LibraryItemModel):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Library CV name cannot be empty")

    try:
        _validate_payload(payload.data)
        items = _load_library()
        item = {
            "id": uuid4().hex,
            "name": name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "data": payload.data,
        }
        items.append(item)
        _save_library(items)
        return item
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.delete("/api/library/{item_id}")
def delete_from_library(item_id: str):
    items = _load_library()
    remaining = [item for item in items if item.get("id") != item_id]
    if len(remaining) == len(items):
        raise HTTPException(status_code=404, detail="Library CV not found")
    _save_library(remaining)
    return {"status": "success"}


@app.post("/api/generate")
def generate_cv(payload: CVDataModel):
    try:
        data = payload.data
        _validate_payload(data)

        output_path = OUTPUT_DIR / CONFIG["output_filename"]
        builder = CVBuilder(data=data, config=CONFIG)
        result_path = Path(builder.build(output_path))
        
        if not result_path.exists():
            raise HTTPException(status_code=500, detail="PDF generation failed to produce a file.")

        _save_cv_data(data)
            
        return FileResponse(
            path=result_path,
            filename=CONFIG["output_filename"],
            media_type="application/pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
