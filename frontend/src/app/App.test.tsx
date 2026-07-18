import { screen } from '@testing-library/react';
import { renderApp } from '../test/renderApp';

describe('TPM Operating System application', () => {
  it('renders the application shell and sidebar', () => {
    renderApp('/programs');

    expect(screen.getByText('TPM Operating System')).toBeInTheDocument();
    expect(screen.getAllByRole('navigation', { name: 'Primary navigation' })).not.toHaveLength(0);
    expect(screen.getAllByRole('link', { name: 'Programs' })).not.toHaveLength(0);
  });

  it('renders the Programs integration-pending state', () => {
    renderApp('/programs');

    expect(screen.getByRole('heading', { level: 1, name: 'Programs' })).toBeInTheDocument();
    expect(screen.getByText(/No program data is currently available because backend integration/)).toBeInTheDocument();
    expect(screen.getByText(/This is an expected application state/)).toBeInTheDocument();
  });

  it('renders the Program Workspace integration-pending state', () => {
    renderApp('/programs/program-123');

    expect(screen.getByRole('heading', { level: 1, name: 'Program Workspace' })).toBeInTheDocument();
    expect(screen.getByText('The Program Workspace will become available after backend integration.')).toBeInTheDocument();
  });

  it('renders Programs at the root application entry', () => {
    renderApp('/');
    expect(screen.getByRole('heading', { level: 1, name: 'Programs' })).toBeInTheDocument();
    expect(screen.getByTestId('current-location')).toHaveTextContent('/programs');
  });

  it('keeps unavailable navigation entries disabled and non-navigable', () => {
    renderApp('/programs');

    for (const label of ['Reports', 'Documents', 'Templates', 'Settings']) {
      const entries = screen.getAllByRole('button', { name: `${label} unavailable` });
      expect(entries.length).toBeGreaterThan(0);
      entries.forEach((entry) => {
        expect(entry).toHaveAttribute('aria-disabled', 'true');
        expect(entry).not.toHaveAttribute('href');
      });
      expect(screen.getByRole('heading', { level: 1, name: 'Programs' })).toBeInTheDocument();
      expect(screen.getByTestId('current-location')).toHaveTextContent('/programs');
    }
  });
});
