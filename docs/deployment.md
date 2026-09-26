# Deployment

The project is best deployed as two Vercel projects from the same repository:

1. A frontend project for `frontend/`.
2. A backend project for the repository root and `api/index.py`.

## Backend Vercel project

Use the repository root as the Vercel Root Directory:

```text
./
```

The root must contain:

```text
api/index.py
server.py
requirements.txt
cv_generator/
cover_letter_maker/
```

Recommended settings:

| Setting          | Value                             |
| ---------------- | --------------------------------- |
| Preset           | FastAPI                           |
| Build command    | None                              |
| Output directory | N/A                               |
| Install command  | `pip install -r requirements.txt` |

`vercel.json` uses the `@vercel/python` runtime and routes requests to `api/index.py`.

Recommended backend environment variables:

```text
VERCEL=1
FRONTEND_URL=https://cv-resume-maker-frontend.vercel.app
```

If Google Drive is enabled, configure the OAuth callback to use the public backend domain:

```text
GOOGLE_DRIVE_REDIRECT_URI=https://YOUR-BACKEND-DOMAIN.vercel.app/api/google-drive/callback
```

Disable Vercel Deployment Protection for public browser API access. If protection is enabled, browser requests receive a `302` redirect to Vercel SSO instead of a FastAPI response, causing CORS errors.

## Frontend Vercel project

Set the Root Directory to:

```text
frontend
```

Recommended settings:

| Setting          | Value           |
| ---------------- | --------------- |
| Framework        | Vite            |
| Build command    | `npm run build` |
| Output directory | `dist`          |
| Install command  | `npm install`   |

Set this environment variable in Vercel:

```text
VITE_API_BASE=https://YOUR-BACKEND-DOMAIN.vercel.app/api
```

After changing `VITE_API_BASE`, redeploy the frontend because Vite embeds environment variables during the build.

## CORS

The backend allows local development origins and the production frontend origin. If you use a custom frontend domain, set `FRONTEND_URL` to that exact origin, including `https://` and without a trailing slash.

## Deployment smoke tests

After deployment, verify:

```text
https://YOUR-BACKEND-DOMAIN.vercel.app/docs
https://YOUR-BACKEND-DOMAIN.vercel.app/openapi.json
https://YOUR-BACKEND-DOMAIN.vercel.app/api/cv
```

The responses must not redirect to `vercel.com/sso-api`.
