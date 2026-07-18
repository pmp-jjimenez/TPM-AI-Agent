# Backend API

The backend exposes a read-only FastAPI interface to the existing TPM Operating
System application. The CLI remains the primary interface. Both interfaces use
the existing program persistence functions in `app/memory.py`; the API does not
read program JSON directly or duplicate persistence and normalization rules.

## Install

From the repository root, install the pinned Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Run

The current persistence path is relative to the process working directory, so
the API must currently be started from the repository root:

```bash
python3 -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

The API is then available at `http://127.0.0.1:8000`. Interactive Swagger UI is
at `http://127.0.0.1:8000/docs`, and the OpenAPI JSON document is at
`http://127.0.0.1:8000/openapi.json`.

Implemented endpoints are:

- `GET /health`
- `GET /programs`
- `GET /programs/{programId}`

The API is intentionally read-only. It does not provide authentication,
authorization, program mutations, search, filtering, sorting, or pagination.

## CORS

The React development origins `http://localhost:5173` and
`http://127.0.0.1:5173` are allowed by default. Add origins with the
comma-separated `TPM_API_CORS_ORIGINS` environment variable:

```bash
TPM_API_CORS_ORIGINS="https://workspace.example.com,https://preview.example.com" \
  python3 -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

Configured values supplement the two defaults. CORS credentials are disabled.

## Architecture and limitations

`backend/api/routers/` owns HTTP routing. `backend/api/dependencies.py` provides
a thin, read-only adapter over `app/memory.py`. `backend/api/compat.py` is the
minimal bridge required by the existing script-oriented imports under `app/`;
it avoids a broad package migration and preserves `python3 app/main.py`.

Program storage remains local JSON under `data/programs/`. Listing programs can
create that directory because this is existing persistence behavior. Atomic
replacement protects normal writes, but there is no cross-process locking,
transaction isolation, database, or multi-user concurrency control. Malformed,
unreadable, or concurrently changed files can cause a structured server error.
Server exceptions are logged without exposing stack traces or filesystem paths
in HTTP responses.

## Tests

Run the API tests from the repository root:

```bash
python3 -m unittest tests.test_api -v
```

The tests use temporary program storage and do not read or modify the real
`data/programs/` contents.
