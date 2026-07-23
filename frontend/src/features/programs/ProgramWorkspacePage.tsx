import { Button, Grid2, Stack, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { ApiError } from '../../api/client';
import { ErrorState } from '../../components/feedback/ErrorState';
import { LoadingState } from '../../components/feedback/LoadingState';
import { PageContainer } from '../../components/layout/PageContainer';
import { SeverityBadge } from '../../components/ui/StatusBadges';
import { SectionHeader } from '../../components/ui/Primitives';
import {
  AIAssessmentCard,
  ExecutiveMetricCard,
  MissionHeader,
  OperationalSection,
  PriorityCard,
  type OperationalItem,
  type PriorityItem,
} from './MissionControlComponents';
import { displayDate } from './dateFormatting';
import { getProgram } from './programApi';
import type { ProgramRecord } from './programTypes';
import { usableText } from './programTypes';

function ownerName(owner: { display_name: string } | null): string | undefined { return owner?.display_name; }
function detail(label: string, value?: string | null) { return { label, value }; }

function riskItems(program: ProgramRecord): OperationalItem[] {
  return (program.risks ?? []).map((risk) => ({
    id: risk.object_id, title: risk.title, status: risk.status,
    badge: risk.priority ? <SeverityBadge value={risk.priority} /> : undefined,
    details: [detail('Status', risk.status), detail('Owner', ownerName(risk.owner)), detail('Probability', risk.probability), detail('Impact', risk.impact), detail('Review', displayDate(risk.review_date)), detail('Mitigation', risk.mitigation_plan), detail('Accepted by', risk.status === 'accepted' ? ownerName(risk.accepted_by) : undefined)],
  }));
}

function issueItems(program: ProgramRecord): OperationalItem[] {
  return (program.issues ?? []).map((issue) => ({
    id: issue.object_id, title: issue.title, status: issue.status,
    badge: issue.severity ? <SeverityBadge value={issue.severity} /> : undefined,
    details: [detail('Status', issue.status), detail('Owner', ownerName(issue.owner)), detail('Due', displayDate(issue.due_date)), detail('Impact', issue.impact), detail('Resolution', issue.resolution_summary), detail('Resolved', displayDate(issue.resolved_at))],
  }));
}

function dependencyItems(program: ProgramRecord): OperationalItem[] {
  return (program.dependencies ?? []).map((dependency) => ({
    id: dependency.object_id, title: dependency.title, status: dependency.status,
    details: [detail('Status', dependency.status), detail('Type', dependency.dependency_type), detail('Owner', ownerName(dependency.owner)), detail('Depends on', dependency.depends_on), detail('External party', dependency.external_party), detail('Required by', displayDate(dependency.required_by_date)), detail('Impact', dependency.impact), detail('Mitigation', dependency.mitigation_plan)],
  }));
}

function decisionItems(program: ProgramRecord): OperationalItem[] {
  return (program.decisions ?? []).map((decision) => ({
    id: decision.object_id, title: decision.title, status: decision.status,
    details: [detail('Status', decision.status), detail('Decision', decision.decision), detail('Rationale', decision.rationale), detail('Owner', ownerName(decision.owner)), detail('Decision date', displayDate(decision.decision_date)), detail('Review date', displayDate(decision.review_date)), detail('Impact', decision.impact), detail('Alternatives considered', decision.alternatives_considered.join('; ') || undefined)],
  }));
}

function actionItems(program: ProgramRecord): OperationalItem[] {
  return (program.next_actions ?? []).map((action) => ({
    id: action.object_id, title: action.title, status: action.status,
    badge: action.priority ? <SeverityBadge value={action.priority} /> : undefined,
    details: [detail('Status', action.status), detail('Owner', ownerName(action.owner)), detail('Due', displayDate(action.due_date)), detail('Description', action.description), detail('Completion summary', action.completion_summary)],
  }));
}

function priorities(program: ProgramRecord): PriorityItem[] {
  const criticalIssue = (program.issues ?? []).find((item) => item.status !== 'closed' && item.status !== 'resolved' && item.severity === 'critical');
  const criticalRisk = (program.risks ?? []).find((item) => item.status !== 'closed' && (item.priority === 'critical' || item.impact === 'critical'));
  const blockedAction = (program.next_actions ?? []).find((item) => item.status === 'blocked');
  const openDependency = (program.dependencies ?? []).find((item) => item.status === 'open' || item.status === 'in_progress');
  const nextAction = (program.next_actions ?? []).find((item) => item.status === 'open' || item.status === 'in_progress');
  const signals: PriorityItem[] = [];
  if (criticalIssue) signals.push({ id: `issue-${criticalIssue.object_id}`, title: `Address issue: ${criticalIssue.title}`, detail: 'A critical open issue requires review.', tone: 'critical' });
  if (criticalRisk) signals.push({ id: `risk-${criticalRisk.object_id}`, title: `Review risk: ${criticalRisk.title}`, detail: criticalRisk.review_date ? `Review date: ${displayDate(criticalRisk.review_date)}` : 'Critical exposure is recorded.', tone: 'critical' });
  if (blockedAction) signals.push({ id: `action-${blockedAction.object_id}`, title: `Unblock action: ${blockedAction.title}`, detail: ownerName(blockedAction.owner) ? `Owner: ${ownerName(blockedAction.owner)}` : 'No owner is recorded.', tone: 'attention' });
  if (openDependency) signals.push({ id: `dependency-${openDependency.object_id}`, title: `Track dependency: ${openDependency.title}`, detail: openDependency.required_by_date ? `Required by ${displayDate(openDependency.required_by_date)}` : 'No required-by date is recorded.', tone: 'attention' });
  if (!signals.length && nextAction) signals.push({ id: `next-${nextAction.object_id}`, title: nextAction.title, detail: nextAction.due_date ? `Due ${displayDate(nextAction.due_date)}` : 'This is the next stored program action.', tone: 'neutral' });
  if (!signals.length) signals.push({ id: 'clear', title: 'No critical blockers detected', detail: 'No critical open issue, risk, or blocked action is recorded.', tone: 'clear' });
  return signals.slice(0, 4);
}

export function ProgramWorkspacePage() {
  const { programId } = useParams();
  const [program, setProgram] = useState<ProgramRecord | null>(null);
  const [error, setError] = useState<unknown>();
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setProgram(null);
    setError(undefined);
    if (!programId?.trim()) {
      setError(new ApiError('malformed', 'A valid program identifier is required.'));
      return () => controller.abort();
    }
    getProgram(programId, controller.signal).then(setProgram).catch((requestError) => {
      if (!(requestError instanceof ApiError && requestError.kind === 'aborted')) setError(requestError);
    });
    return () => controller.abort();
  }, [programId, requestVersion]);

  const retry = <Button variant="outlined" onClick={() => setRequestVersion((value) => value + 1)}>Retry</Button>;
  if (error instanceof ApiError && error.status === 404) return <PageContainer><ErrorState title="Program not found." message="The requested program is not available." action={<Button component={RouterLink} to="/programs" variant="contained">Return to Programs</Button>} /></PageContainer>;
  if (error) return <PageContainer><ErrorState title={error instanceof ApiError && error.kind === 'configuration' ? 'API configuration required' : 'Program could not be loaded'} message={error instanceof ApiError && error.kind === 'configuration' ? error.message : error instanceof ApiError && error.kind === 'network' ? 'Check your connection and confirm the API is running, then try again.' : 'The server could not load this program. Please try again.'} action={error instanceof ApiError && error.kind === 'configuration' ? undefined : retry} /></PageContainer>;
  if (!program) return <PageContainer><LoadingState message="Loading program mission control" /></PageContainer>;

  const risks = riskItems(program);
  const issues = issueItems(program);
  const dependencies = dependencyItems(program);
  const decisions = decisionItems(program);
  const actions = actionItems(program);
  const collectionCount = risks.length + issues.length + dependencies.length + decisions.length + actions.length;

  return (
    <PageContainer>
      <Stack spacing={{ xs: 4.5, md: 6 }}>
        <MissionHeader name={usableText(program.program_name) ?? 'Program name unavailable'} description={usableText(program.description)} programId={program.program_id} phase={usableText(program.phase)} health={usableText(program.health)} confidence={usableText(program.confidence)} updatedAt={displayDate(program.metadata?.updated_at)} />

        <Stack component="section" spacing={2.25} aria-label="Executive health summary">
          <SectionHeader title="Executive Health Summary" description="The current reported state of this program." />
          <Grid2 container spacing={2} data-testid="program-health-grid">
            <Grid2 size={{ xs: 12, sm: 6, lg: 3 }}><ExecutiveMetricCard label="Program Health" value={usableText(program.health) ?? '—'} supportingText="Reported health" /></Grid2>
            <Grid2 size={{ xs: 12, sm: 6, lg: 3 }}><ExecutiveMetricCard label="Confidence" value={usableText(program.confidence) ?? '—'} supportingText="Reported confidence" /></Grid2>
            <Grid2 size={{ xs: 12, sm: 6, lg: 3 }}><ExecutiveMetricCard label="Lifecycle Phase" value={usableText(program.phase) ?? '—'} supportingText="Current program phase" /></Grid2>
            <Grid2 size={{ xs: 12, sm: 6, lg: 3 }}><ExecutiveMetricCard label="Collections" value={collectionCount} supportingText="Operational records" /></Grid2>
          </Grid2>
        </Stack>

        <Grid2 container spacing={2.5} alignItems="stretch">
          <Grid2 size={{ xs: 12, md: 5 }}><PriorityCard items={priorities(program)} /></Grid2>
          <Grid2 size={{ xs: 12, md: 7 }}><AIAssessmentCard /></Grid2>
        </Grid2>

        <Stack spacing={{ xs: 4.5, md: 6 }} component="section" aria-labelledby="operational-workspace-title">
          <BoxTitle />
          <OperationalSection title="Risks" description="Threats to delivery outcomes and their current treatment." items={risks} emptyMessage="No canonical risks are stored for this program." />
          <OperationalSection title="Issues" description="Active delivery problems requiring resolution." items={issues} emptyMessage="No canonical issues are stored for this program." />
          <OperationalSection title="Dependencies" description="Internal and external commitments affecting delivery." items={dependencies} emptyMessage="No canonical dependencies are stored for this program." />
          <OperationalSection title="Decision Records" description="Program decisions and their recorded rationale." items={decisions} emptyMessage="No decision records are stored for this program." />
          <OperationalSection title="Actions" description="Committed next steps and accountable owners." items={actions} emptyMessage="No program actions are stored for this program." />
        </Stack>
      </Stack>
    </PageContainer>
  );
}

function BoxTitle() {
  return <Stack spacing={0.5}><Typography id="operational-workspace-title" component="h2" variant="sectionTitle">Operational Workspace</Typography><Typography variant="supporting" color="text.secondary">Read-only program records organized for rapid operational review.</Typography></Stack>;
}
