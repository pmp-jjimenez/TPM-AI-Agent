# TPM Operating System Frontend

The frontend is a production React application that provides the browser shell and client-side routing for TPM Operating System. Program data is intentionally unavailable until a backend API is integrated.

## Requirements

- Node.js 18 or newer
- npm 8 or newer

## Installation

From `frontend/`, install the exact dependency tree recorded in `package-lock.json`:

```bash
npm ci
```

## Development

Start the Vite development server:

```bash
npm run dev
```

The terminal output shows the local URL. Vite defaults to `http://localhost:5173` when that port is available.

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
- Material UI provides accessible primitives and a restrained, centralized theme.
- The sidebar becomes a temporary drawer on smaller screens and remains visible on desktop.
- Only Programs is enabled. Other navigation entries are rendered as disabled controls and do not have routes.
- No API client, network call, local persistence adapter, or mock data is present. Integration infrastructure will be added only after a backend contract exists.
- The application states explicitly describe the current lack of backend integration rather than fabricating runtime information.
