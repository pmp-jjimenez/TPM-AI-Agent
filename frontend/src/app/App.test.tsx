import { fireEvent, screen, waitFor, within } from '@testing-library/react';
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
  metadata: { created_at: '2026-06-01T00:00:00Z', updated_at: '2026-07-17T00:00:00Z', source: 'test' },
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
  it('renders loading and then the executive workspace with real identity, status, and supported summary fields', async () => {
    let resolveRequest!: (value: Response) => void;
    vi.spyOn(globalThis, 'fetch').mockReturnValue(new Promise((resolve) => { resolveRequest = resolve; }));
    renderApp('/programs/alpha-program');
    expect(screen.getByRole('status')).toHaveTextContent('Loading program workspace');

    resolveRequest(jsonResponse(alpha));
    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha Program' })).toBeInTheDocument();
    expect(screen.getByText('Program ID: alpha-program')).toBeInTheDocument();
    expect(screen.getByText('Alpha description Customer: Alpha customer. Current phase: Delivery. Health: Green. Confidence: High.')).toBeInTheDocument();
    expect(screen.getAllByText('Green')).toHaveLength(2);
    expect(screen.getByText('Jul 17, 2026')).toBeInTheDocument();
    expect(screen.getByText('test')).toBeInTheDocument();
    expect(screen.queryByText('Kickoff')).not.toBeInTheDocument();
  });

  it('states when supported information is insufficient and ignores malformed optional fields', async () => {
    mockFetchOnce({ program_id: 'alpha-program', program_name: 'Alpha', health: 4, milestones: [null, 'bad', {}, { title: 4 }], next_actions: [null, {}, 7], metadata: [] });
    renderApp('/programs/alpha-program');

    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha' })).toBeInTheDocument();
    expect(screen.getByText('Available program information is insufficient to provide an executive summary.')).toBeInTheDocument();
    expect(screen.getByText('No milestones recorded')).toBeInTheDocument();
    expect(screen.getByText('No stored program actions are available.')).toBeInTheDocument();
  });

  it('keeps Unknown as a real status value and detects only absent completeness fields', async () => {
    mockFetchOnce({
      ...alpha,
      health: 'Unknown',
      sponsor: 'Unknown',
      budget: 0,
      target_go_live: 'Unknown',
      architecture: { summary: 'Unknown' },
      dependencies: ['Unknown'],
      governance: 'Unknown',
    });
    renderApp('/programs/alpha-program');

    expect(await screen.findAllByText('Unknown')).toHaveLength(2);
    expect(screen.getByText('All executive completeness fields are recorded.')).toBeInTheDocument();
    expect(screen.queryByText('Collect executive program information')).not.toBeInTheDocument();
  });

  it('shows missing executive information and deterministic Program Initiation recommendations', async () => {
    mockFetchOnce({ ...alpha, phase: 'Program Initiation' });
    renderApp('/programs/alpha-program');

    expect(await screen.findByText('These details are not recorded. They are not risks or issues.')).toBeInTheDocument();
    for (const field of ['Sponsor', 'Budget', 'Target Go-Live', 'Architecture', 'Dependencies', 'Governance']) {
      expect(screen.getByText(field)).toBeInTheDocument();
    }
    expect(screen.getByText('Internal Technical Kickoff')).toBeInTheDocument();
    expect(screen.getByText('Collect executive program information')).toBeInTheDocument();
  });

  it('renders explicit milestones and never substitutes meeting history', async () => {
    mockFetchOnce({
      ...alpha,
      milestones: [null, 'bad', { name: 'Architecture Review', target_date: '2026-08-10', status: 'Scheduled' }, { title: 3 }],
    });
    renderApp('/programs/alpha-program');

    expect(await screen.findByText('Architecture Review')).toBeInTheDocument();
    expect(screen.getByText('Aug 10, 2026')).toBeInTheDocument();
    expect(screen.getByText('Status: Scheduled')).toBeInTheDocument();
    expect(screen.queryByText('Kickoff')).not.toBeInTheDocument();
  });

  it('keeps stored next actions distinct from workspace recommendations and preserves explicit metadata', async () => {
    mockFetchOnce({
      ...alpha,
      phase: 'Program Initiation',
      next_actions: [
        'Confirm rollout cohort',
        { action: 'Review support model', status: 'Open', owner: 'Operations', due_date: '2026-08-01' },
        { description: 7 },
      ],
    });
    renderApp('/programs/alpha-program');

    const storedHeading = await screen.findByRole('heading', { level: 3, name: 'Stored Program Actions' });
    const recommendationHeading = screen.getByRole('heading', { level: 3, name: 'Workspace Recommendations' });
    expect(storedHeading.compareDocumentPosition(screen.getByText('Confirm rollout cohort')) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(recommendationHeading.compareDocumentPosition(screen.getByText('Internal Technical Kickoff')) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.getByText('Status: Open')).toBeInTheDocument();
    expect(screen.getByText('Owner: Operations')).toBeInTheDocument();
    expect(screen.getByText('Due: 2026-08-01')).toBeInTheDocument();
  });

  it('declares single-column narrow breakpoints for executive status sections', async () => {
    mockFetchOnce(alpha);
    renderApp('/programs/alpha-program');

    const headerGrid = await screen.findByTestId('executive-header-status-grid');
    const healthGrid = screen.getByTestId('program-health-grid');
    expect(within(headerGrid).getAllByText(/Current Phase|Health|Confidence/)).toHaveLength(3);
    expect(headerGrid.querySelectorAll('.MuiGrid2-grid-xs-12')).toHaveLength(3);
    expect(healthGrid.querySelectorAll('.MuiGrid2-grid-xs-12')).toHaveLength(3);
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
