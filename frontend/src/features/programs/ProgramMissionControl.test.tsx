import { screen, within } from '@testing-library/react';
import { renderApp } from '../../test/renderApp';

const program = {
  program_id: 'alpha-program',
  program_name: 'Alpha Program',
  description: 'Enterprise platform rollout',
  phase: 'Execution',
  health: 'Amber',
  confidence: 'Medium',
  metadata: { updated_at: '2026-07-22T00:00:00Z' },
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

function canonicalDependency() {
  return {
    object_id: '66666666-6666-4666-8666-666666666666', object_type: 'dependency', title: 'Vendor circuit',
    description: null, owner: { display_name: 'Network Lead', stakeholder_id: null }, lifecycle_phase: 'execution',
    audit: { created_at: null, updated_at: null, source: 'legacy_import' }, status: 'open', dependency_type: 'vendor',
    depends_on: 'Carrier delivery', external_party: 'Example Carrier', required_by_date: '2026-08-01',
    impact: 'Cutover blocked', mitigation_plan: 'Escalate weekly',
  };
}

const audit = { created_at: null, updated_at: null, source: 'legacy_import' };
const owner = { display_name: 'Delivery Lead', stakeholder_id: null };

function operationalProgram() {
  return {
    ...program,
    risks: [{
      object_id: '22222222-2222-4222-8222-222222222222', object_type: 'risk', title: 'Cutover exposure',
      description: null, owner, lifecycle_phase: 'execution', audit, status: 'open', probability: 'high',
      impact: 'critical', priority: 'critical', mitigation_plan: 'Run rehearsal', contingency_plan: null,
      review_date: '2026-07-25', acceptance_rationale: null, accepted_by: null,
    }],
    issues: [{
      object_id: '44444444-4444-4444-8444-444444444444', object_type: 'issue', title: 'Access blocked',
      description: null, owner, lifecycle_phase: 'execution', audit, status: 'blocked', severity: 'critical',
      impact: 'Testing stopped', due_date: '2026-07-24', resolution_summary: null, resolved_at: null, root_cause: null,
    }],
    dependencies: [canonicalDependency()],
    decisions: [{
      object_id: '88888888-8888-4888-8888-888888888888', object_type: 'decision_record', title: 'Approve rollout',
      decision: 'Use waves', rationale: 'Reduce exposure', alternatives_considered: ['Big bang'], owner,
      status: 'approved', decision_date: '2026-07-22', review_date: null, impact: 'Two waves', audit,
      lifecycle_phase: 'execution',
    }],
    next_actions: [{
      object_id: '11111111-1111-4111-8111-111111111111', object_type: 'action', title: 'Unblock access',
      description: null, status: 'blocked', priority: 'critical', owner, lifecycle_phase: 'execution',
      due_date: '2026-07-24', completed_at: null, completion_summary: null, audit,
    }],
  };
}

describe('Program Mission Control', () => {
  it('renders a focused Mission Header with identity, status badges, and update context', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse(program));
    renderApp('/programs/alpha-program');

    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha Program' })).toBeInTheDocument();
    expect(screen.getByText('Enterprise platform rollout')).toBeInTheDocument();
    expect(screen.getByLabelText('Phase: Execution')).toBeInTheDocument();
    expect(screen.getByLabelText('Health: At Risk')).toBeInTheDocument();
    expect(screen.getByLabelText('Confidence: Medium')).toBeInTheDocument();
    expect(screen.getByText('Last updated: Jul 22, 2026')).toBeInTheDocument();
  });

  it('renders all executive metric cards from reported data without invented values', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse(program));
    renderApp('/programs/alpha-program');

    const summary = await screen.findByRole('region', { name: 'Executive health summary' });
    expect(within(summary).getByRole('article', { name: 'Program Health' })).toHaveTextContent('Amber');
    expect(within(summary).getByRole('article', { name: 'Confidence' })).toHaveTextContent('Medium');
    expect(within(summary).getByRole('article', { name: 'Lifecycle Phase' })).toHaveTextContent('Execution');
    expect(within(summary).getByRole('article', { name: 'Collections' })).toHaveTextContent('0');
  });

  it('derives critical priorities from stored issues, risks, blocked actions, and dependencies', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse(operationalProgram()));
    renderApp('/programs/alpha-program');

    const priorities = await screen.findByRole('region', { name: "Today's Priorities" });
    expect(within(priorities).getByText('Address issue: Access blocked')).toBeInTheDocument();
    expect(within(priorities).getByText('Review risk: Cutover exposure')).toBeInTheDocument();
    expect(within(priorities).getByText('Unblock action: Unblock access')).toBeInTheDocument();
    expect(within(priorities).getByText('Track dependency: Vendor circuit')).toBeInTheDocument();
  });

  it('renders populated Risks, Issues, Dependencies, Decision Records, and Actions sections', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse(operationalProgram()));
    renderApp('/programs/alpha-program');

    const expected = [
      ['Risks', 'Cutover exposure'], ['Issues', 'Access blocked'], ['Dependencies', 'Vendor circuit'],
      ['Decision Records', 'Approve rollout'], ['Actions', 'Unblock access'],
    ];
    for (const [sectionName, itemName] of expected) {
      const section = await screen.findByRole('region', { name: sectionName });
      expect(within(section).getByRole('article', { name: itemName })).toBeInTheDocument();
      expect(within(section).getByLabelText(`${sectionName}: 1 records`)).toBeInTheDocument();
    }
  });

  it('provides named, counted empty states for every operational section', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse(program));
    renderApp('/programs/alpha-program');

    for (const sectionName of ['Risks', 'Issues', 'Dependencies', 'Decision Records', 'Actions']) {
      const section = await screen.findByRole('region', { name: sectionName });
      expect(within(section).getByLabelText(`${sectionName}: 0 records`)).toBeInTheDocument();
      expect(within(section).getByText(`No ${sectionName.toLowerCase()} recorded`)).toBeInTheDocument();
    }
  });

  it('communicates identity, executive state, priorities, and AI availability without a live AI request', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse(program));
    renderApp('/programs/alpha-program');

    expect(screen.getByRole('status')).toHaveTextContent('Loading program mission control');
    expect(await screen.findByRole('heading', { level: 1, name: 'Alpha Program' })).toBeInTheDocument();
    expect(screen.getAllByText('Program Mission Control')).toHaveLength(2);
    expect(screen.getByText('Enterprise platform rollout')).toBeInTheDocument();
    expect(screen.getByLabelText('Health: At Risk')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: 'Executive Health Summary' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: "Today's Priorities" })).toBeInTheDocument();
    expect(screen.getByText('No critical blockers detected')).toBeInTheDocument();
    expect(screen.getByRole('heading', { level: 2, name: 'AI Assessment' })).toBeInTheDocument();
    expect(screen.getByText('Awaiting grounded program intelligence')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /intelligence/i })).not.toBeInTheDocument();
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });

  it('organizes all operational collections with counts and useful empty states', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse({ ...program, dependencies: [canonicalDependency()] }));
    renderApp('/programs/alpha-program');

    expect(await screen.findByRole('heading', { level: 2, name: 'Operational Workspace' })).toBeInTheDocument();
    for (const title of ['Risks', 'Issues', 'Dependencies', 'Decision Records', 'Actions']) {
      expect(screen.getByRole('heading', { level: 2, name: title })).toBeInTheDocument();
    }
    expect(screen.getByLabelText('Dependencies: 1 records')).toBeInTheDocument();
    expect(screen.getByText('Vendor circuit')).toBeInTheDocument();
    expect(screen.getByText('Track dependency: Vendor circuit')).toBeInTheDocument();
    expect(screen.getByText('No risks recorded')).toBeInTheDocument();
    expect(screen.getByText('No actions recorded')).toBeInTheDocument();
  });

  it('declares mobile-first metric and operational card layouts', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(jsonResponse({ ...program, dependencies: [canonicalDependency()] }));
    renderApp('/programs/alpha-program');

    const metrics = await screen.findByTestId('program-health-grid');
    expect(metrics.querySelectorAll('.MuiGrid2-grid-xs-12')).toHaveLength(4);
    const dependencySection = screen.getByRole('region', { name: 'Dependencies' });
    expect(within(dependencySection).getByRole('article', { name: 'Vendor circuit' })).toBeInTheDocument();
    expect(dependencySection.querySelector('.MuiGrid2-grid-xs-12')).toBeInTheDocument();
  });
});
