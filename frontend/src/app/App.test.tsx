import { fireEvent, screen, waitFor } from '@testing-library/react';
import { renderApp } from '../test/renderApp';

const alpha = {
  program_id: 'alpha-program',
  program_name: 'Alpha Program',
  description: 'Alpha description',
  customer: 'Alpha customer',
  phase: 'Delivery',
  health: 'Green',
  confidence: 'High',
  meeting_history: [{ date: '2026-07-01', title: 'Kickoff', description: 'Program kickoff' }],
  metadata: { created_at: '2026-06-01T00:00:00Z', updated_at: '2026-07-17T00:00:00Z' },
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

function mockFetchOnce(body: unknown, status = 200) {
  return vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse(body, status));
}

describe('Programs page', () => {
  it('renders the shell and a loading state while programs are requested', () => {
    vi.spyOn(globalThis, 'fetch').mockReturnValue(new Promise(() => {}));
    renderApp('/programs');

    expect(screen.getByText('TPM Operating System')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('Loading programs');
  });

  it('renders valid programs alphabetically without mutating or crashing on malformed entries', async () => {
    const missing = { program_id: 'missing-fields', program_name: 42, phase: null, metadata: 'invalid' };
    mockFetchOnce([{ program_id: '', program_name: 'Invalid' }, { ...alpha, program_id: 'zulu', program_name: 'Zulu' }, missing, alpha]);
    renderApp('/programs');

    const headings = await screen.findAllByRole('heading', { level: 2 });
    expect(headings.map((heading) => heading.textContent)).toEqual(['—', 'Alpha Program', 'Zulu']);
    expect(screen.getAllByText('—').length).toBeGreaterThanOrEqual(3);
    expect(screen.queryByText('Invalid')).not.toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith('https://api.test/programs', expect.objectContaining({ method: 'GET' }));
  });

  it('renders an empty state for an empty response', async () => {
    mockFetchOnce([]);
    renderApp('/programs');
    expect(await screen.findByText('No programs available')).toBeInTheDocument();
  });

  it('handles a network failure and retries', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockRejectedValueOnce(new TypeError('offline'))
      .mockResolvedValueOnce(jsonResponse([alpha]));
    renderApp('/programs');

    expect(await screen.findByText('Programs are unavailable')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Retry' }));
    expect(await screen.findByText('Alpha Program')).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it('shows a production error for HTTP 500 without exposing backend content', async () => {
    mockFetchOnce({ error: { code: 'program_persistence_error', message: '/private/data failed\nstack trace' } }, 500);
    renderApp('/programs');

    expect(await screen.findByText('Programs could not be loaded')).toBeInTheDocument();
    expect(screen.queryByText(/private\/data/)).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Retry' })).toBeInTheDocument();
  });

  it('navigates to the encoded selected program route', async () => {
    const program = { ...alpha, program_id: 'program / one' };
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse([program]))
      .mockResolvedValueOnce(jsonResponse(program));
    renderApp('/programs');

    fireEvent.click(await screen.findByRole('link', { name: /Alpha Program/ }));
    await waitFor(() => expect(screen.getByTestId('current-location')).toHaveTextContent('/programs/program%20%2F%20one'));
  });
});

describe('Program workspace', () => {
  it('renders loading and then real workspace data', async () => {
    let resolveRequest!: (value: Response) => void;
    vi.spyOn(globalThis, 'fetch').mockReturnValue(new Promise((resolve) => { resolveRequest = resolve; }));
    renderApp('/programs/alpha-program');
    expect(screen.getByRole('status')).toHaveTextContent('Loading program workspace');

    resolveRequest(jsonResponse(alpha));
    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha Program' })).toBeInTheDocument();
    expect(screen.getByText('Alpha description')).toBeInTheDocument();
    expect(screen.getByText('Green')).toBeInTheDocument();
    expect(screen.getByText('Kickoff')).toBeInTheDocument();
    expect(screen.getByText('2026-07-17T00:00:00Z')).toBeInTheDocument();
  });

  it('ignores malformed optional fields without crashing', async () => {
    mockFetchOnce({ program_id: 'alpha-program', program_name: 'Alpha', health: 4, meeting_history: [null, 'bad', {}], metadata: [] });
    renderApp('/programs/alpha-program');

    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha' })).toBeInTheDocument();
    expect(screen.getByText('No supported timeline entries are available.')).toBeInTheDocument();
    expect(screen.getAllByText('Health')).toHaveLength(2);
  });

  it('renders a structured 404 and returns to Programs', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse({ error: { code: 'program_not_found', message: "Program 'missing' was not found." } }, 404))
      .mockResolvedValueOnce(jsonResponse([]));
    renderApp('/programs/missing');

    expect(await screen.findByText('Program not found.')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('link', { name: 'Return to Programs' }));
    await waitFor(() => expect(screen.getByTestId('current-location')).toHaveTextContent('/programs'));
    expect(await screen.findByText('No programs available')).toBeInTheDocument();
  });

  it('aborts the request when the workspace unmounts', () => {
    let capturedSignal: AbortSignal | undefined;
    vi.spyOn(globalThis, 'fetch').mockImplementation((_input, init) => {
      capturedSignal = init?.signal ?? undefined;
      return new Promise(() => {});
    });
    const view = renderApp('/programs/alpha-program');
    expect(capturedSignal?.aborted).toBe(false);
    view.unmount();
    expect(capturedSignal?.aborted).toBe(true);
  });
});
