# CV Studio Documentation

CV Studio is a Python/FastAPI and React/Vite application for creating ATS-friendly CVs and professional cover letters.

## Documentation map

- [Getting started](getting-started.md) — install, configure, and run the project locally.
- [Architecture](architecture.md) — backend, frontend, document generation, and signature processing.
- [API reference](api.md) — important FastAPI endpoints and request behavior.
- [Deployment](deployment.md) — deploy the frontend and backend as separate Vercel projects.
- [Privacy and storage](privacy.md) — temporary files, generated documents, and production considerations.

## Main features

- Structured CV editor with reusable sections.
- ATS-focused PDF CV generation.
- CV PDF import for selectable text.
- Cover-letter editor with templates and live preview.
- Cover-letter PDF import and editable extracted fields.
- Handwritten signature upload and printable signature template workflow.
- Local CV library and optional Google Drive storage.

## Local URLs

| Service               | URL                                |
| --------------------- | ---------------------------------- |
| React frontend        | http://localhost:5173              |
| FastAPI backend       | http://127.0.0.1:8000              |
| Swagger documentation | http://127.0.0.1:8000/docs         |
| OpenAPI schema        | http://127.0.0.1:8000/openapi.json |

Always review imported data before generating a final document.
