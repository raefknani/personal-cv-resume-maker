# Architecture

## Repository layout

```text
.
├── api/index.py                 Vercel FastAPI entrypoint
├── server.py                    FastAPI application and routes
├── cv_generator/                CV data, validation, styling, and renderer
├── cover_letter_maker/          Cover-letter models, import, renderer, and signatures
├── frontend/                    React/Vite application
├── tests/                       Backend and document-generation tests
├── docs/                        Project documentation
├── requirements.txt             Python dependencies
└── vercel.json                  Backend Vercel runtime and routing
```

## Backend

`server.py` creates the FastAPI application. It exposes CV, library, Google Drive, cover-letter, and signature routes.

`cv_generator.builder.CVBuilder` renders ATS-friendly CV PDFs with ReportLab.

`cover_letter_maker.renderer.CoverLetterRenderer` renders searchable cover-letter PDFs and inserts an already-processed signature image. It does not perform image extraction.

`cover_letter_maker.signature.SignatureProcessor` validates image bytes, applies EXIF orientation, extracts dark foreground pixels, creates an alpha mask, crops transparent margins, and returns a confidence score.

`cover_letter_maker.pdf_import` extracts selectable text from uploaded PDFs using `pypdf` and maps common cover-letter fields.

## Frontend

The React application is a single-page editor. CV and cover-letter data are held in component state and sent to the FastAPI API with `fetch`.

The Cover Letter workspace includes:

- Details, Content, and Signature steps.
- Live preview.
- CV data reuse.
- PDF import.
- Signature preview and sizing controls.
- Template selection.

## Data flow

```text
React form
   │
   ├── GET/POST CV data ────────► FastAPI
   ├── upload PDF ──────────────► PDF importer
   ├── upload signature ─────────► Signature processor ──► temporary PNG
   └── generate PDF ─────────────► ReportLab renderer ───► PDF download
```

## Storage model

Local development uses JSON files for CV data and the library. Temporary signatures are written to `temp/signatures/`.

When `VERCEL=1`, runtime files are redirected to `/tmp/pdf-creator` because the Vercel deployment filesystem is not persistent. Production applications should use a database and private object storage.
