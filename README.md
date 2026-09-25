The web app loads the built-in CV data initially, saves edits to `saved_data.json`, and downloads generated PDFs from the FastAPI backend. The original `python -m cv_generator.main` CLI remains available.

### Optional Google Drive storage

The Library tab can also save and load CV versions in Google Drive. Local JSON storage continues to work without Google Drive.

1. In Google Cloud Console, create a project, enable the **Google Drive API**, and configure an OAuth consent screen.
2. Create an OAuth client for a **Web application** and add this redirect URI:
   `http://127.0.0.1:8000/api/google-drive/callback`
3. Download the client JSON as `credentials.json` into the project root.
4. Restart the backend, open the Library tab, and click **Connect Google Drive**.

The app requests only the `drive.file` scope and stores files in Drive's private application-data folder. The OAuth token is saved as `.google-drive-token.json`; do not commit either credentials file.

# Modular CV Generator

This project generates a professional ATS-friendly PDF CV from a centralized data model while preserving a modular architecture.

## Project structure

- `cv_generator/` contains the data, styling, rendering, validation, and PDF builder logic.
- `tests/` contains the automated validation and generation checks.
- `cv_generator/output/` stores the generated PDF file.

## Installation

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\activate
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

## Generate the CV

```bash
python -m cv_generator.main
```

The generated file is written to:

```text
cv_generator/output/CV_Raef_Knani_ATS.pdf
```

The default template is the standard ATS format: single-column layout, clean section headings, and plain text styling for better parsing by recruiters and applicant tracking systems.

## Use the web application

Install the Python dependencies and frontend dependencies once, then start the backend and frontend in separate terminals.

Backend:

```powershell
.venv\Scripts\activate
uvicorn server:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the frontend terminal (normally `http://localhost:5173`). The web app loads the built-in CV data initially, saves edits to `saved_data.json`, and downloads generated PDFs from the FastAPI backend. The original `python -m cv_generator.main` CLI remains available.

## Cover Letter Maker

The **Cover Letter** tab supports structured cover letters, reusable CV data, editable text-based PDF import, multiple templates, handwritten signature upload, printable signature templates, transparent PNG previews, and searchable final PDFs.

Signature images are kept in the local `temp/signatures/` directory with randomized names. They are not public assets. Production deployments should add authentication, ownership checks, TTL cleanup, and encrypted private storage before enabling persistent signature assets.

The backend provides `/api/cover-letters/import-pdf`, `/api/cover-letters/generate`, `/api/signatures/template`, `/api/signatures/process-upload`, `/api/signatures/process-template`, and `/api/signatures/{id}/preview`.

The processor accepts PNG/JPEG, corrects EXIF orientation, removes light backgrounds, crops transparent margins, and returns a confidence score. The generated PDF keeps cover-letter text searchable and inserts only the processed signature image.

Use the **Library** tab to save named CV versions, load the latest versions for editing, or delete old versions. Each editor section has a **Clear** button that resets only that section. **Load Demo CV** fills the editor with safe sample values that can be replaced with your own information.

The **Load from PDF** control in the Library tab imports selectable text from an existing CV PDF and maps common sections into the editor. Review the imported fields before saving. Scanned or image-only PDFs are not supported yet because they require OCR.

### Optional Google Drive storage

The Library tab can also save and load CV versions in Google Drive. Local JSON storage continues to work without Google Drive.

1. In Google Cloud Console, create a project, enable the **Google Drive API**, and configure an OAuth consent screen.
2. Create an OAuth client for a **Web application** and add this redirect URI: `http://127.0.0.1:8000/api/google-drive/callback`.
3. Download the client JSON as `credentials.json` into the project root.
4. Restart the backend, open the Library tab, and click **Connect Google Drive**.

The app requests only the `drive.file` scope and stores files in Drive's private application-data folder. The OAuth token is saved as `.google-drive-token.json`; do not commit either credentials file.

## Modify personal data

Edit the data in `cv_generator/data/cv_data.py`.

Example:

```python
CV_DATA["personal"]["title"] = "Software Engineer"
```

## Add an experience entry

Append to the `experience` list in `cv_generator/data/cv_data.py`:

```python
CV_DATA["experience"].append({
    "position": "Developer",
    "company": "Example Company",
    "location": "Tunisia",
    "start_date": "2024",
    "end_date": "2025",
    "description": ["Built a product feature."]
})
```

## Add a project

Append to the `projects` list in `cv_generator/data/cv_data.py`:

```python
CV_DATA["projects"].append({
    "name": "Project Name",
    "technologies": "Python, FastAPI",
    "description": ["Delivered a functional application."]
})
```

## Change styling

Update the visual settings in `cv_generator/styles/styles.py`.

## Disable sections

Set entries in `cv_generator/config.py` such as:

```python
CONFIG["include_projects"] = False
```

## Create a CV variant

Use `cv_generator/variants/general.py` with `apply_variant`.

Example:

```python
variant = {"title": "Software Engineer", "section_order": ["profile", "experience"]}
updated = apply_variant(CV_DATA, variant)
```

## Run tests

```bash
pytest
```
