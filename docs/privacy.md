# Privacy and storage

CVs, cover letters, uploaded PDFs, and handwritten signatures can contain sensitive personal information.

## Current behavior

- CV data is stored locally in `saved_data.json`.
- The local CV library is stored in `cv_library.json`.
- Processed signatures are stored temporarily in `temp/signatures/`.
- Generated local PDFs are written under the configured output directory.
- Signature preview files use randomized temporary IDs.
- Signature images are not intended to be public assets.
- Final signature PNG metadata is minimized by re-encoding with Pillow.

## Google Drive

Google Drive support uses the private `appDataFolder` scope. OAuth credentials and tokens must remain outside version control.

Never commit:

```text
.env
credentials.json
.google-drive-token.json
saved_data.json
cv_library.json
```

## Production requirements

The current local JSON and temporary-file implementation is suitable for development and demos. A production deployment should add:

- User authentication.
- Ownership checks for every CV and signature asset.
- A database such as PostgreSQL or Supabase.
- Private object storage for uploaded files.
- Short-lived signed URLs.
- Automatic temporary asset cleanup.
- Upload rate limits and processing timeouts.
- Encryption at rest.
- Audit-safe, non-sensitive logging.

Vercel serverless storage under `/tmp` is ephemeral. It must not be treated as permanent storage.
