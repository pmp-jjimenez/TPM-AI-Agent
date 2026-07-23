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

function canonicalRisk(overrides: Record<string, unknown> = {}) {
  return {
    object_id: '22222222-2222-4222-8222-222222222222', object_type: 'risk', title: 'Stored delivery risk',
    description: null, owner: null, lifecycle_phase: 'initiation',
    audit: { created_at: null, updated_at: null, source: 'legacy_import' },
    status: 'open', probability: null, impact: null, priority: null, mitigation_plan: null,
    contingency_plan: null, review_date: null, acceptance_rationale: null, accepted_by: null, ...overrides,
  };
}

function canonicalIssue(overrides: Record<string, unknown> = {}) {
  return {
    object_id: '44444444-4444-4444-8444-444444444444', object_type: 'issue', title: 'Stored access issue',
    description: null, owner: null, lifecycle_phase: 'execution',
    audit: { created_at: null, updated_at: null, source: 'legacy_import' },
    status: 'open', severity: null, impact: null, due_date: null,
    resolution_summary: null, resolved_at: null, root_cause: null, ...overrides,
  };
}

function canonicalDependency(overrides: Record<string, unknown> = {}) {
  return {
    object_id: '66666666-6666-4666-8666-666666666666', object_type: 'dependency', title: 'Vendor circuit',
    description: null, owner: { display_name: 'Network Lead', stakeholder_id: null }, lifecycle_phase: 'execution',
    audit: { created_at: null, updated_at: null, source: 'legacy_import' }, status: 'open',
    dependency_type: 'vendor', depends_on: 'Carrier delivery', external_party: 'Example Carrier',
    required_by_date: '2026-08-01', impact: 'Cutover blocked', mitigation_plan: 'Escalate weekly', ...overrides,
  };
}

function canonicalDecision(overrides: Record<string, unknown> = {}) {
  return {
    object_id: '88888888-8888-4888-8888-888888888888', object_type: 'decision_record',
    title: 'Approve staged rollout', decision: 'Use three deployment waves',
    rationale: 'Limits operational exposure', alternatives_considered: ['Big bang'],
    owner: { display_name: 'Program Sponsor', stakeholder_id: null }, status: 'approved',
    decision_date: '2026-07-22', review_date: '2026-08-22', impact: 'Timeline extends by two weeks',
    audit: { created_at: null, updated_at: null, source: 'legacy_import' }, lifecycle_phase: 'execution',
    ...overrides,
  };
}

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

    expect(screen.getAllByText('TPM Operating System').length).toBeGreaterThan(0);
    expect(screen.getAllByRole('navigation', { name: 'Primary navigation' }).length).toBeGreaterThan(0);
    expect(screen.getAllByText('Executive Review').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Major Incidents').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Operational Readiness').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Reports').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Settings').length).toBeGreaterThan(0);
    expect(screen.getByLabelText('Future workspace actions')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('Loading programs');
  });

  it('renders valid programs alphabetically without mutating or crashing on malformed entries', async () => {
    const missing = { program_id: 'missing-fields', program_name: 42, phase: null, metadata: 'invalid' };
    mockFetchOnce([{ program_id: '', program_name: 'Invalid' }, { ...alpha, program_id: 'zulu', program_name: 'Zulu' }, missing, alpha]);
    renderApp('/programs');

    expect(await screen.findByRole('heading', { level: 1, name: 'TPM Command Center' })).toBeInTheDocument();
    expect(screen.getByText(/Good Morning|Good Afternoon/)).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: 'Portfolio Summary' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: "Today's Focus" })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: 'AI Advisor' })).toBeInTheDocument();
    expect(screen.getByText('Confidence: HIGH')).toBeInTheDocument();
    expect(screen.getByRole('article', { name: 'Active Programs: 3' })).toBeInTheDocument();
    const headings = screen.getAllByRole('heading', { level: 3 });
    expect(headings.map((heading) => heading.textContent)).toEqual(['—', 'Alpha Program', 'Zulu']);
    expect(screen.getAllByText('—').length).toBeGreaterThanOrEqual(2);
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
    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha Program' })).toBeInTheDocument();
    expect(screen.getAllByText('Program Mission Control')).toHaveLength(2);
  });
});

describe('Program Mission Control integration', () => {
  it('renders loading and then the executive workspace with real identity, status, and supported summary fields', async () => {
    let resolveRequest!: (value: Response) => void;
    vi.spyOn(globalThis, 'fetch').mockReturnValue(new Promise((resolve) => { resolveRequest = resolve; }));
    renderApp('/programs/alpha-program');
    expect(screen.getByRole('status')).toHaveTextContent('Loading program mission control');

    resolveRequest(jsonResponse(alpha));
    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha Program' })).toBeInTheDocument();
    expect(screen.getByText('Program ID: alpha-program')).toBeInTheDocument();
    expect(screen.getByText('Alpha description')).toBeInTheDocument();
    expect(screen.getByLabelText('Health: Healthy')).toBeInTheDocument();
    expect(screen.getByText('Last updated: Jul 17, 2026')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: 'Executive Health Summary' })).toBeInTheDocument();
    expect(screen.queryByText('Kickoff')).not.toBeInTheDocument();
  });

  it('states when supported information is insufficient and ignores malformed optional fields', async () => {
    mockFetchOnce({ program_id: 'alpha-program', program_name: 'Alpha', health: 4, milestones: [null, 'bad', {}, { title: 4 }], next_actions: [null, {}, 7], metadata: [] });
    renderApp('/programs/alpha-program');

    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha' })).toBeInTheDocument();
    expect(screen.getByText('No program description is available.')).toBeInTheDocument();
    expect(screen.getByText('No actions recorded')).toBeInTheDocument();
    expect(screen.getByText('No risks recorded')).toBeInTheDocument();
  });

  it('shows a structured AI placeholder without making an intelligence request', async () => {
    const fetchSpy = mockFetchOnce(alpha);
    renderApp('/programs/alpha-program');

    expect(await screen.findByRole('heading', { level: 2, name: 'AI Assessment' })).toBeInTheDocument();
    expect(screen.getByText('Awaiting grounded program intelligence')).toBeInTheDocument();
    expect(screen.getByText('No recommendation available')).toBeInTheDocument();
    expect(screen.getByText('No watch item identified')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /intelligence/i })).not.toBeInTheDocument();
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  it('does not surface out-of-scope milestones or substitute meeting history', async () => {
    mockFetchOnce({ ...alpha, milestones: [{ name: 'Architecture Review' }] });
    renderApp('/programs/alpha-program');

    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha Program' })).toBeInTheDocument();
    expect(screen.queryByText('Architecture Review')).not.toBeInTheDocument();
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

    const actionsSection = await screen.findByRole('region', { name: 'Actions' });
    expect(within(actionsSection).getByText('Confirm rollout cohort')).toBeInTheDocument();
    expect(screen.queryByText('Internal Technical Kickoff')).not.toBeInTheDocument();
    expect(within(actionsSection).getAllByText('Status')).toHaveLength(2);
    expect(within(actionsSection).getByText('Operations')).toBeInTheDocument();
    expect(within(actionsSection).getByText('Aug 1, 2026')).toBeInTheDocument();
  });

  it('renders strict canonical stored risks and their optional treatment details', async () => {
    mockFetchOnce({
      ...alpha,
      risks: [canonicalRisk({
        owner: { display_name: 'Change Lead', stakeholder_id: null }, probability: 'high', impact: 'critical',
        priority: 'high', review_date: '2026-08-15', mitigation_plan: 'Run readiness reviews',
        status: 'accepted', acceptance_rationale: 'Exposure is within tolerance',
        accepted_by: { display_name: 'Executive Sponsor', stakeholder_id: null },
      })],
    });
    renderApp('/programs/alpha-program');
    const risksSection = await screen.findByRole('region', { name: 'Risks' });
    expect(within(risksSection).getByText('Stored delivery risk')).toBeInTheDocument();
    expect(within(risksSection).getByText('Change Lead')).toBeInTheDocument();
    expect(within(risksSection).getByText('high')).toBeInTheDocument();
    expect(within(risksSection).getByText('critical')).toBeInTheDocument();
    expect(within(risksSection).getByText('Run readiness reviews')).toBeInTheDocument();
    expect(within(risksSection).getByText('Executive Sponsor')).toBeInTheDocument();
  });

  it('rejects a malformed canonical stored risk payload', async () => {
    mockFetchOnce({ ...alpha, risks: [canonicalRisk({ status: 'invented' })] });
    renderApp('/programs/alpha-program');
    expect(await screen.findByText('Program could not be loaded')).toBeInTheDocument();
    expect(screen.queryByText('Stored delivery risk')).not.toBeInTheDocument();
  });

  it('renders strict canonical stored issues and optional closure details', async () => {
    mockFetchOnce({ ...alpha, issues: [canonicalIssue({
      status: 'closed', owner: { display_name: 'Operations', stakeholder_id: null },
      due_date: '2026-08-01', severity: 'high', impact: 'Cutover blocked',
      resolution_summary: 'Access granted', resolved_at: '2026-07-22T12:00:00Z',
    })] });
    renderApp('/programs/alpha-program');
    const issuesSection = await screen.findByRole('region', { name: 'Issues' });
    expect(within(issuesSection).getByText('Stored access issue')).toBeInTheDocument();
    expect(within(issuesSection).getByText('Operations')).toBeInTheDocument();
    expect(screen.getByLabelText('Severity: High')).toBeInTheDocument();
    expect(within(issuesSection).getByText('Access granted')).toBeInTheDocument();
  });

  it('rejects a malformed canonical stored issue payload', async () => {
    mockFetchOnce({ ...alpha, issues: [canonicalIssue({ due_date: 'soon' })] });
    renderApp('/programs/alpha-program');
    expect(await screen.findByText('Program could not be loaded')).toBeInTheDocument();
    expect(screen.queryByText('Stored access issue')).not.toBeInTheDocument();
  });

  it('strictly parses and renders canonical stored dependencies read-only', async () => {
    mockFetchOnce({ ...alpha, dependencies: [canonicalDependency()] });
    renderApp('/programs/alpha-program');
    const dependenciesSection = await screen.findByRole('region', { name: 'Dependencies' });
    expect(within(dependenciesSection).getByText('Vendor circuit')).toBeInTheDocument();
    expect(within(dependenciesSection).getByText('vendor')).toBeInTheDocument();
    expect(within(dependenciesSection).getByText('Network Lead')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /edit dependency/i })).not.toBeInTheDocument();
  });

  it('rejects malformed canonical stored dependencies', async () => {
    mockFetchOnce({ ...alpha, dependencies: [canonicalDependency({ required_by_date: 'soon' })] });
    renderApp('/programs/alpha-program');
    expect(await screen.findByText('Program could not be loaded')).toBeInTheDocument();
    expect(screen.queryByText('Vendor circuit')).not.toBeInTheDocument();
  });

  it('strictly parses and renders decision records read-only', async () => {
    mockFetchOnce({ ...alpha, decisions: [canonicalDecision()] });
    renderApp('/programs/alpha-program');
    expect(await screen.findByRole('heading', { level: 2, name: 'Decision Records' })).toBeInTheDocument();
    expect(screen.getByText('Approve staged rollout')).toBeInTheDocument();
    expect(screen.getByText('Use three deployment waves')).toBeInTheDocument();
    expect(screen.getByText('Limits operational exposure')).toBeInTheDocument();
    expect(screen.getByText('Big bang')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /edit decision/i })).not.toBeInTheDocument();
  });

  it('rejects malformed canonical decision records', async () => {
    mockFetchOnce({ ...alpha, decisions: [canonicalDecision({ status: 'final' })] });
    renderApp('/programs/alpha-program');
    expect(await screen.findByText('Program could not be loaded')).toBeInTheDocument();
    expect(screen.queryByText('Approve staged rollout')).not.toBeInTheDocument();
  });

  it('declares single-column narrow breakpoints for executive status sections', async () => {
    mockFetchOnce(alpha);
    renderApp('/programs/alpha-program');

    const healthGrid = await screen.findByTestId('program-health-grid');
    expect(within(healthGrid).getByText('Program Health')).toBeInTheDocument();
    expect(within(healthGrid).getByText('Confidence')).toBeInTheDocument();
    expect(within(healthGrid).getByText('Lifecycle Phase')).toBeInTheDocument();
    expect(within(healthGrid).getByText('Collections')).toBeInTheDocument();
    expect(healthGrid.querySelectorAll('.MuiGrid2-grid-xs-12')).toHaveLength(4);
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
