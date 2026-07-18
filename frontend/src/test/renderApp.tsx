import { CssBaseline, ThemeProvider } from '@mui/material';
import { render } from '@testing-library/react';
import { MemoryRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { NotFoundPage } from '../features/not-found/NotFoundPage';
import { ProgramWorkspacePage } from '../features/programs/ProgramWorkspacePage';
import { ProgramsPage } from '../features/programs/ProgramsPage';
import { theme } from '../app/theme';

export function renderApp(initialPath = '/') {
  function LocationObserver() {
    const location = useLocation();
    return <span data-testid="current-location" hidden>{location.pathname}</span>;
  }

  return render(
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <MemoryRouter initialEntries={[initialPath]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <LocationObserver />
        <Routes>
          <Route path="/" element={<AppShell />}>
            <Route index element={<Navigate to="/programs" replace />} />
            <Route path="programs" element={<ProgramsPage />} />
            <Route path="programs/:programId" element={<ProgramWorkspacePage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </MemoryRouter>
    </ThemeProvider>,
  );
}
