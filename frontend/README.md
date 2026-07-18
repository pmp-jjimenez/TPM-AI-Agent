# TPM Operating System Frontend

The frontend is a production React application that retrieves read-only program data from the FastAPI API. The request path is React → FastAPI → the existing JSON persistence service; the browser never reads persistence files directly.

## Requirements

- Node.js 18 or newer
- npm 8 or newer

## Installation

From `frontend/`, install the exact dependency tree recorded in `package-lock.json`:

```bash
npm ci
```

## Development

From the repository root, start the backend API. The working directory is required because persistence resolves `data/programs/` relative to it:

```bash
python3 -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000
```

The API is then available at `http://127.0.0.1:8000`. Its current scope is read-only: `GET /health`, `GET /programs`, and `GET /programs/{programId}`. Authentication and authorization are not implemented.

In a second terminal, start the frontend with the required API base URL:

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

The frontend is available at `http://localhost:5173` when Vite's default port is free. `VITE_API_BASE_URL` must be one absolute HTTP or HTTPS URL. A trailing slash is accepted and normalized; credentials, queries, and fragments are rejected. Missing or invalid configuration produces a clear application error rather than making a request. There is no alternate API configuration source.

Other commands:

```bash
npm run typecheck  # Check TypeScript without emitting files
npm test           # Run the frontend test suite once
npm run build      # Type-check and create a production build
npm run preview    # Serve the production build locally
```

## Folder structure

```text
src/
├── app/          # Application composition, routes, and theme
├── components/   # Reusable layout and feedback components
├── features/     # Feature-owned pages and presentation
├── test/         # Shared test setup and render helpers
└── main.tsx      # Browser entry point
```

## Architecture decisions

- Routes are declared in `src/app/routes.tsx` and render inside one reusable application shell.
- Program pages live in a feature directory; reusable layout and feedback components remain domain-neutral.
- `src/api/config.ts` owns API configuration, while `src/api/client.ts` owns GET transport, safe JSON parsing, cancellation, and structured failures.
- Material UI provides accessible primitives and a restrained, centralized theme.
- The sidebar becomes a temporary drawer on smaller screens and remains visible on desktop.
- Only Programs is enabled. Other navigation entries are rendered as disabled controls and do not have routes.
- The Programs page fetches `GET /programs`; selecting a valid record navigates to its encoded route and fetches `GET /programs/{programId}`.
- Loading, empty, offline, server-error, malformed-response, and not-found states remain usable. Network and server failures offer retry; workspace 404 responses offer a return to Programs.
- API records are parsed defensively. Missing optional values are not replaced with domain defaults, and malformed list entries without a usable `program_id` are omitted.

## Current limitations

- `GET /programs` returns full program records rather than list summaries, which may increase payload size as records grow.
- The API contract intentionally remains flexible and persistence may apply compatibility defaults before returning records.
- The frontend is read-only and has no authentication, editing, search, filtering, or pagination.
