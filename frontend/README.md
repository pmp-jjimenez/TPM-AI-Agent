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

## Executive program workspace

The program workspace is executive-first: identity and reported status appear before supporting metadata, completeness gaps, and next steps. It is intentionally an information and decision-support surface rather than a JSON viewer or decorative dashboard. It does not calculate KPIs, composite health, percentages, or inferred RAG status.

The workspace keeps stored facts separate from deterministic recommendations:

- The executive summary uses only the stored program name, description, customer, phase, health, and confidence. If a usable description is unavailable, the workspace states that the available information is insufficient.
- Program Health repeats only the API-provided phase, health, and confidence. `Unknown` is displayed as a real value with restrained uncertainty styling; it is not treated as missing or as a failure.
- Project Overview displays customer, description, metadata source, and timestamps. Unambiguous ISO dates are formatted for readability; other usable date text is preserved.
- Timeline displays only usable records from an explicit `milestones` collection. It never converts `meeting_history` into milestones and shows a professional empty state when milestones are absent or malformed.
- Missing Information checks the explicit sponsor, budget, target go-live, architecture, dependencies, and governance values. Only absent, null, empty, or unusable values are listed. The literal value `Unknown` counts as recorded information, and completeness gaps are not presented as risks or issues.
- Stored `next_actions` are shown separately from workspace recommendations. Legacy strings and supported object shapes are parsed defensively. The workspace recommends `Internal Technical Kickoff` only for the exact `Program Initiation` phase and recommends collecting the specifically missing completeness fields.

These rules run entirely in the browser over the existing API response. They do not call an AI model, persist recommendations, create actions, or modify program data.

The workspace uses wrapping metadata grids and breakpoint-aware cards. Status cards, overview metadata, next-step columns, and other multi-column content collapse to a single column on narrow screens without changing the existing responsive sidebar behavior.

## Current limitations

- `GET /programs` returns full program records rather than list summaries, which may increase payload size as records grow.
- The API contract intentionally remains flexible and persistence may apply compatibility defaults before returning records.
- The frontend is read-only and has no authentication, editing, search, filtering, or pagination.
- Milestones and executive completeness fields are not part of the canonical Program Data Foundation v1 schema. They appear only when explicitly present in an API record; consequently, current records commonly show an empty timeline and completeness gaps.
- Workspace recommendations are limited to local deterministic rules. There is no AI-generated workspace summary, prioritization, or next-best-action intelligence.
