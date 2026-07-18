import { Navigate, createBrowserRouter } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { NotFoundPage } from '../features/not-found/NotFoundPage';
import { ProgramWorkspacePage } from '../features/programs/ProgramWorkspacePage';
import { ProgramsPage } from '../features/programs/ProgramsPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/programs" replace /> },
      { path: 'programs', element: <ProgramsPage /> },
      { path: 'programs/:programId', element: <ProgramWorkspacePage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);
