# Getting started

## Requirements

- Python 3.10 or newer.
- Node.js 18 or newer.
- npm.

## Backend setup

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Start FastAPI:

```powershell
uvicorn server:app --reload
```

The backend is available at `http://127.0.0.1:8000`.

## Frontend setup

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

The frontend uses the local API automatically on localhost. To override it, create `frontend/.env.local`:

```text
VITE_API_BASE=http://127.0.0.1:8000/api
```

Do not commit `.env.local` or secrets.

## Generate a CV from the CLI

```powershell
python -m cv_generator.main
```

## Run tests

```powershell
pytest
```

## Build the frontend

```powershell
cd frontend
npm run build
```

## Common workflows

### CV

1. Open the Personal, Profile, Skills, Experience, Projects, Education, or Other tab.
2. Edit the structured fields.
3. Save the data or save a named version in Library.
4. Select Generate PDF.

### Cover letter

1. Open Cover Letter.
2. Fill Details and Content, or use information from the CV.
3. Optionally import a selectable-text cover-letter PDF.
4. Upload a signature or download the printable signature template.
5. Review the live preview.
6. Select Download PDF.
