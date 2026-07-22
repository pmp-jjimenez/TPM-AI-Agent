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

function canonicalAction(overrides: Record<string, unknown> = {}) {
  return {
    object_id: '11111111-1111-4111-8111-111111111111',
    object_type: 'action',
    title: 'Confirm rollout cohort',
    description: null,
    status: 'open',
    priority: null,
    owner: null,
    lifecycle_phase: 'initiation',
    due_date: null,
    completed_at: null,
    completion_summary: null,
    audit: { created_at: null, updated_at: null, source: 'legacy_import' },
    ...overrides,
  };
}

const aiIntelligence = {
  schema_version: '1.0.0',
  program_id: 'alpha-program',
  generated_at: '2026-07-17T12:00:00Z',
  source: 'ai',
  routing: {
    version: '1.0.0',
    primary_persona: { id: 'technical_program_manager', display_name: 'Technical Program Manager' },
    supporting_personas: [{ id: 'delivery_manager', display_name: 'Delivery Manager' }],
  },
  summary: 'Grounded AI intelligence summary.',
  confidence: 'High',
  findings: [
    { id: 'fnd_1111111111111111', category: 'risk', statement: 'Stored delivery risk', confidence: 'High', evidence_refs: ['/risks/0'], impact: 'Delivery may be affected.' },
    { id: 'fnd_2222222222222222', category: 'dependency', statement: 'Vendor delivery is required.', confidence: 'Medium', evidence_refs: ['/dependencies/0'] },
  ],
  recommendations: [{ id: 'rec_3333333333333333', priority: 'High', statement: 'Review delivery plan', rationale: 'The recorded risk requires a controlled response.', evidence_refs: ['/risks/0'], related_finding_ids: ['fnd_1111111111111111'] }],
  decisions_required: [{ id: 'dec_4444444444444444', priority: 'Medium', statement: 'Confirm risk treatment.', reason: 'Delivery direction is required.', related_finding_ids: ['fnd_1111111111111111'], related_recommendation_ids: ['rec_3333333333333333'] }],
  next_action: { id: 'act_5555555555555555', priority: 'High', statement: 'Review the delivery plan now.', rationale: 'This is the highest-priority supported action.', related_finding_ids: ['fnd_1111111111111111'], related_recommendation_ids: ['rec_3333333333333333'] },
  limitations: [],
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

  it('shows a not-generated state and makes no intelligence request on workspace load', async () => {
    const fetchSpy = mockFetchOnce(alpha);
    renderApp('/programs/alpha-program');

    expect(await screen.findByText('Intelligence has not been generated for this workspace session.')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Generate Intelligence' })).toBeEnabled();
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  it('generates AI intelligence once, displays personas and grounded sections, then allows refresh', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse(alpha))
      .mockResolvedValueOnce(jsonResponse(aiIntelligence))
      .mockResolvedValueOnce(jsonResponse({ ...aiIntelligence, summary: 'Refreshed intelligence.' }));
    renderApp('/programs/alpha-program');

    fireEvent.click(await screen.findByRole('button', { name: 'Generate Intelligence' }));
    expect(await screen.findByText('Grounded AI intelligence summary.')).toBeInTheDocument();
    expect(screen.getByText('AI')).toBeInTheDocument();
    expect(screen.getByText('Technical Program Manager')).toBeInTheDocument();
    expect(screen.getByText('Delivery Manager')).toBeInTheDocument();
    expect(screen.getByText('Stored delivery risk')).toBeInTheDocument();
    expect(screen.getByText('Risks')).toBeInTheDocument();
    expect(screen.getByText('Dependencies')).toBeInTheDocument();
    expect(screen.getByText('Review delivery plan')).toBeInTheDocument();
    expect(screen.getByText('The recorded risk requires a controlled response.')).toBeInTheDocument();
    expect(screen.getByText('Confirm risk treatment.')).toBeInTheDocument();
    expect(screen.getByText('Delivery direction is required.')).toBeInTheDocument();
    expect(screen.getByText('Review the delivery plan now.')).toBeInTheDocument();
    expect(screen.getAllByText('Evidence: /risks/0')).toHaveLength(2);
    expect(screen.getByText('1.0.0')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Refresh Intelligence' }));
    expect(await screen.findByText('Refreshed intelligence.')).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledTimes(3);
  });

  it('displays deterministic fallback and limitations distinctly', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse(alpha))
      .mockResolvedValueOnce(jsonResponse({
        ...aiIntelligence,
        source: 'deterministic_fallback',
        confidence: 'Medium',
        summary: 'Grounded deterministic summary.',
        limitations: ['AI generation was unavailable; grounded deterministic intelligence is shown.'],
      }));
    renderApp('/programs/alpha-program');
    fireEvent.click(await screen.findByRole('button', { name: 'Generate Intelligence' }));
    expect(await screen.findByText('Deterministic Fallback')).toBeInTheDocument();
    expect(screen.getByText(/AI generation was unavailable/)).toBeInTheDocument();
  });

  it('prevents duplicate requests while generation is active', async () => {
    let resolveIntelligence!: (response: Response) => void;
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse(alpha))
      .mockImplementationOnce(() => new Promise((resolve) => { resolveIntelligence = resolve; }));
    renderApp('/programs/alpha-program');
    const button = await screen.findByRole('button', { name: 'Generate Intelligence' });
    fireEvent.click(button);
    expect(screen.getByRole('button', { name: 'Generating Intelligence…' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Generating Intelligence…' }));
    expect(fetch).toHaveBeenCalledTimes(2);
    resolveIntelligence(jsonResponse(aiIntelligence));
    expect(await screen.findByText('Grounded AI intelligence summary.')).toBeInTheDocument();
  });

  it('keeps workspace facts visible on intelligence failure and retries safely', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse(alpha))
      .mockRejectedValueOnce(new TypeError('private network detail'))
      .mockResolvedValueOnce(jsonResponse(aiIntelligence));
    renderApp('/programs/alpha-program');
    fireEvent.click(await screen.findByRole('button', { name: 'Generate Intelligence' }));
    expect(await screen.findByText('Intelligence is unavailable')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 1, name: 'Alpha Program' })).toBeInTheDocument();
    expect(screen.queryByText('private network detail')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Retry Intelligence' }));
    expect(await screen.findByText('Grounded AI intelligence summary.')).toBeInTheDocument();
  });

  it('rejects malformed nested intelligence and invalid evidence references', async () => {
    const malformed = { ...aiIntelligence, findings: [{ ...aiIntelligence.findings[0], evidence_refs: ['not-a-pointer'] }] };
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse(alpha)).mockResolvedValueOnce(jsonResponse(malformed));
    renderApp('/programs/alpha-program');
    fireEvent.click(await screen.findByRole('button', { name: 'Generate Intelligence' }));
    expect(await screen.findByText('Intelligence is unavailable')).toBeInTheDocument();
    expect(screen.queryByText('Stored delivery risk')).not.toBeInTheDocument();
  });

  it('rejects relationships to IDs absent from the same result', async () => {
    const malformed = { ...aiIntelligence, next_action: { ...aiIntelligence.next_action, related_finding_ids: ['fnd_aaaaaaaaaaaaaaaa'] } };
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse(alpha)).mockResolvedValueOnce(jsonResponse(malformed));
    renderApp('/programs/alpha-program');
    fireEvent.click(await screen.findByRole('button', { name: 'Generate Intelligence' }));
    expect(await screen.findByText('Intelligence is unavailable')).toBeInTheDocument();
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

  it('keeps stored next actions distinct from generated intelligence and preserves explicit metadata', async () => {
    mockFetchOnce({
      ...alpha,
      phase: 'Program Initiation',
      next_actions: [
        canonicalAction(),
        canonicalAction({
          object_id: '22222222-2222-4222-8222-222222222222',
          title: 'Review support model',
          status: 'in_progress',
          owner: { display_name: 'Operations', stakeholder_id: null },
          due_date: '2026-08-01',
        }),
      ],
    });
    renderApp('/programs/alpha-program');

    const storedHeading = await screen.findByRole('heading', { level: 2, name: 'Stored Program Actions' });
    expect(storedHeading.compareDocumentPosition(screen.getByText('Confirm rollout cohort')) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(screen.queryByText('Internal Technical Kickoff')).not.toBeInTheDocument();
    expect(screen.getByText('Status: open')).toBeInTheDocument();
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

  it('aborts an active intelligence request on unmount', async () => {
    let intelligenceSignal: AbortSignal | undefined;
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse(alpha))
      .mockImplementationOnce((_input, init) => {
        intelligenceSignal = init?.signal ?? undefined;
        return new Promise(() => {});
      });
    const view = renderApp('/programs/alpha-program');
    fireEvent.click(await screen.findByRole('button', { name: 'Generate Intelligence' }));
    expect(intelligenceSignal?.aborted).toBe(false);
    view.unmount();
    expect(intelligenceSignal?.aborted).toBe(true);
  });

  it('ignores an intelligence response that resolves after its workspace is gone', async () => {
    let resolveStale!: (response: Response) => void;
    vi.spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse(alpha))
      .mockImplementationOnce(() => new Promise((resolve) => { resolveStale = resolve; }))
      .mockResolvedValueOnce(jsonResponse({ ...alpha, program_id: 'beta-program', program_name: 'Beta Program' }));
    const first = renderApp('/programs/alpha-program');
    fireEvent.click(await screen.findByRole('button', { name: 'Generate Intelligence' }));
    first.unmount();
    renderApp('/programs/beta-program');
    expect(await screen.findByRole('heading', { level: 1, name: 'Beta Program' })).toBeInTheDocument();
    resolveStale(jsonResponse(aiIntelligence));
    await waitFor(() => expect(screen.queryByText('Grounded AI intelligence summary.')).not.toBeInTheDocument());
  });
});
