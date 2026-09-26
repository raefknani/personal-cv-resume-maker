# CV Studio frontend

This directory contains the React/Vite frontend for CV Studio.

## Development

```powershell
npm install
npm run dev
```

The frontend uses `http://127.0.0.1:8000/api` automatically on localhost. To configure another backend, create `.env.local`:

```text
VITE_API_BASE=https://your-backend-domain.example/api
```

## Production build

```powershell
npm run build
```

The output is written to `dist/`.

## Vercel

Deploy this directory as the frontend project:

- Root Directory: `frontend`
- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist`
- Environment variable: `VITE_API_BASE`

See [`../docs/deployment.md`](../docs/deployment.md) for the complete frontend/backend deployment setup.
