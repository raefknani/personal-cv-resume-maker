# CV Studio

> A professional workspace for creating polished, ATS-friendly CVs and cover letters as searchable PDF documents.

CV Studio combines a structured document editor with reusable CV data, PDF import, template-based rendering, handwritten signature support, and a modern React interface.

## ✨ What it does

### Build a professional CV

- Edit personal information, profile, skills, experience, projects, education, certifications, and languages.
- Add and remove skills as organized chips.
- Save named versions in the local CV library.
- Import an existing selectable-text CV PDF.
- Generate ATS-friendly, searchable PDFs.

### Create a cover letter

- Reuse information from the CV with one action.
- Fill a guided Details → Content → Signature workflow.
- Import an existing cover-letter PDF into editable fields.
- Choose Classic, Modern, Minimal, or ATS styling.
- Review changes through a live document preview.

### Add a handwritten signature

- Upload a PNG or JPEG signature.
- Download a printable signature template.
- Process a scanned or photographed signature.
- Remove light backgrounds and transparent margins.
- Resize and align the signature before PDF generation.
- Keep the typed name below the signature image.

## 🧭 User experience

```text
Choose a document
    ↓
Edit structured information
    ↓
Reuse CV data or import a PDF
    ↓
Select a template
    ↓
Preview the document
    ↓
Generate a searchable PDF
```

The application is designed so that technical processing—PDF extraction, signature cleanup, rendering, and temporary file handling—stays behind a simple editor interface.

## 🏗️ Architecture

```text
React + Vite frontend
      │
      ▼
      FastAPI API
      ┌─────┼─────┐
      ▼     ▼     ▼
  CV data  PDF   Signature
  editor   import processing
      └─────┼─────┘
        ▼
       ReportLab PDFs
```

| Area                 | Technology          | Responsibility                                   |
| -------------------- | ------------------- | ------------------------------------------------ |
| Frontend             | React, Vite, Lucide | Editor, workflow, preview, uploads               |
| API                  | FastAPI, Pydantic   | HTTP routes and request handling                 |
| CV generation        | ReportLab           | ATS-friendly searchable CV PDFs                  |
| PDF import           | pypdf               | Text extraction and field mapping                |
| Signature processing | Pillow, NumPy       | Orientation, foreground extraction, transparency |
| Testing              | pytest              | Validation, PDF, import, and signature tests     |

## 📁 Project structure

```text
.
├── api/index.py                # Vercel FastAPI entrypoint
├── server.py                   # FastAPI application
├── cv_generator/               # CV models, validation, styles, renderer
├── cover_letter_maker/         # Cover-letter and signature modules
├── frontend/                   # React/Vite application
├── tests/                      # Automated backend and PDF tests
├── docs/                       # Detailed project documentation
├── requirements.txt            # Python dependencies
└── vercel.json                 # Backend deployment configuration
```

## 🚀 Quick start

### Backend

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` after both services are running.

### CLI PDF generation

```powershell
python -m cv_generator.main
```

### Tests

```powershell
pytest
```

## 🌐 Deployment

The recommended deployment uses two Vercel projects:

| Project  | Root directory  | Purpose                              |
| -------- | --------------- | ------------------------------------ |
| Frontend | `frontend`      | React/Vite interface                 |
| Backend  | repository root | FastAPI, PDF generation, and uploads |

Set the frontend environment variable to the public backend API:

```text
VITE_API_BASE=https://your-backend-domain.vercel.app/api
```

See the complete [deployment guide](docs/deployment.md) for Vercel settings, CORS, environment variables, and smoke tests.

## 📚 Documentation

- [Documentation home](docs/README.md)
- [Getting started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [API reference](docs/api.md)
- [Deployment guide](docs/deployment.md)
- [Privacy and storage](docs/privacy.md)

## 🔐 Privacy notes

Signature images and uploaded documents are sensitive assets. Local development uses temporary files and JSON storage. Production deployments should add authentication, ownership checks, encrypted private storage, database persistence, signed URLs, and automatic cleanup.

Vercel serverless storage is ephemeral and should not be treated as permanent storage.

## 🛣️ Roadmap

- User accounts and document ownership.
- Persistent database-backed CV and cover-letter versions.
- Private object storage for signature assets.
- OCR support for scanned PDFs.
- More cover-letter templates.
- Advanced signature template detection with perspective correction.

## License

Add your preferred license before publishing the project publicly.
