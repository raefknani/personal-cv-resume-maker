# API reference

The local API base URL is `http://127.0.0.1:8000/api`.

## CV endpoints

| Method | Endpoint      | Purpose                               |
| ------ | ------------- | ------------------------------------- |
| GET    | `/cv`         | Load current CV data.                 |
| POST   | `/cv`         | Validate and save CV data.            |
| POST   | `/generate`   | Generate and download a CV PDF.       |
| POST   | `/import-pdf` | Import selectable text from a CV PDF. |

## Library endpoints

| Method | Endpoint             | Purpose                   |
| ------ | -------------------- | ------------------------- |
| GET    | `/library`           | List saved CV snapshots.  |
| POST   | `/library`           | Save a named CV snapshot. |
| DELETE | `/library/{item_id}` | Delete a saved snapshot.  |

## Cover-letter endpoints

| Method | Endpoint                    | Purpose                                          |
| ------ | --------------------------- | ------------------------------------------------ |
| GET    | `/cover-letters/default`    | Return the default cover-letter model.           |
| POST   | `/cover-letters/import-pdf` | Extract editable fields from a PDF cover letter. |
| POST   | `/cover-letters/generate`   | Generate and download a cover-letter PDF.        |

The cover-letter generation body uses:

```json
{
  "data": {
    "personal": {},
    "application": {},
    "content": {},
    "signature": {},
    "template": {}
  }
}
```

## Signature endpoints

| Method | Endpoint                             | Purpose                                        |
| ------ | ------------------------------------ | ---------------------------------------------- |
| GET    | `/signatures/template`               | Download the printable signature template PDF. |
| POST   | `/signatures/process-upload`         | Process a direct PNG/JPEG signature upload.    |
| POST   | `/signatures/process-template`       | Process a scanned or photographed template.    |
| GET    | `/signatures/{signature_id}/preview` | View the temporary processed PNG.              |
| DELETE | `/signatures/{signature_id}`         | Delete a temporary signature asset.            |

Accepted direct signature formats are PNG and JPEG. The recommended maximum upload size is 10 MB.

## Google Drive endpoints

| Method | Endpoint                        | Purpose                                          |
| ------ | ------------------------------- | ------------------------------------------------ |
| GET    | `/google-drive/status`          | Check whether Drive is configured and connected. |
| GET    | `/google-drive/connect`         | Start OAuth authorization.                       |
| GET    | `/google-drive/callback`        | Complete OAuth authorization.                    |
| GET    | `/google-drive/files`           | List private application-data files.             |
| GET    | `/google-drive/files/{file_id}` | Load a saved CV JSON file.                       |
| POST   | `/google-drive/files`           | Save a CV JSON file.                             |

## Interactive API documentation

When the backend is running, use:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

## Error handling

Errors are returned as JSON, normally with a `detail` field. The frontend should display the detail when available and should not assume that an upload or generation request succeeded based only on a network response.
