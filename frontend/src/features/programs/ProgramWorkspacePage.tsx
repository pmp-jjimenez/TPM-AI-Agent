import { Box, Button, Divider, Grid2, Paper, Stack, Typography } from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { ApiError } from '../../api/client';
import { ErrorState } from '../../components/feedback/ErrorState';
import { LoadingState } from '../../components/feedback/LoadingState';
import { PageContainer } from '../../components/layout/PageContainer';
import {
  MetadataGrid,
  IntelligenceResult,
  SectionHeader,
  StatusCard,
} from './ExecutiveWorkspaceComponents';
import { getProgram, getProgramIntelligence } from './programApi';
import type { IntelligenceResponse, ProgramAction, ProgramDecisionRecord, ProgramDependency, ProgramIssue, ProgramRecord, ProgramRisk } from './programTypes';
import { usableText } from './programTypes';

interface Milestone { date?: string; title: string; description?: string; status?: string }
function milestones(program: ProgramRecord): Milestone[] {
  return (program.milestones ?? []).flatMap((entry) => {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) return [];
    const record = entry as Record<string, unknown>;
    const title = usableText(record.title) ?? usableText(record.name);
    if (!title) return [];
    return [{
      title,
      date: usableText(record.date) ?? usableText(record.target_date),
      description: usableText(record.description),
      status: usableText(record.status),
    }];
  });
}

function storedActions(program: ProgramRecord): ProgramAction[] { return program.next_actions ?? []; }
function storedRisks(program: ProgramRecord): ProgramRisk[] { return program.risks ?? []; }
function storedIssues(program: ProgramRecord): ProgramIssue[] { return program.issues ?? []; }
function storedDependencies(program: ProgramRecord): ProgramDependency[] { return program.dependencies ?? []; }
function storedDecisions(program: ProgramRecord): ProgramDecisionRecord[] { return program.decisions ?? []; }

function displayDate(value: unknown): string | undefined {
  const text = usableText(value);
  if (!text) return undefined;
  if (!/^\d{4}-\d{2}-\d{2}(?:T.*)?$/.test(text)) return text;
  const parsed = new Date(text);
  if (Number.isNaN(parsed.getTime())) return text;
  return new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' }).format(parsed);
}

function executiveSummary(program: ProgramRecord): string {
  const description = usableText(program.description);
  if (!description) return 'Available program information is insufficient to provide an executive summary.';
  const facts = [
    usableText(program.customer) ? `Customer: ${usableText(program.customer)}.` : undefined,
    usableText(program.phase) ? `Current phase: ${usableText(program.phase)}.` : undefined,
    usableText(program.health) ? `Health: ${usableText(program.health)}.` : undefined,
    usableText(program.confidence) ? `Confidence: ${usableText(program.confidence)}.` : undefined,
  ].filter(Boolean).join(' ');
  return `${description}${facts ? ` ${facts}` : ''}`;
}

function WorkspaceSection({ children, title, description }: { children: ReactNode; title: string; description?: string }) {
  return (
    <Stack component="section" spacing={2}>
      <SectionHeader title={title} description={description} />
      {children}
    </Stack>
  );
}

export function ProgramWorkspacePage() {
  const { programId } = useParams();
  const [program, setProgram] = useState<ProgramRecord | null>(null);
  const [error, setError] = useState<unknown>();
  const [requestVersion, setRequestVersion] = useState(0);
  const [intelligence, setIntelligence] = useState<IntelligenceResponse | null>(null);
  const [intelligenceError, setIntelligenceError] = useState(false);
  const [intelligenceLoading, setIntelligenceLoading] = useState(false);
  const intelligenceSequence = useRef(0);
  const intelligenceController = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    setProgram(null);
    setError(undefined);
    if (!programId?.trim()) {
      setError(new ApiError('malformed', 'A valid program identifier is required.'));
      return () => controller.abort();
    }
    getProgram(programId, controller.signal)
      .then(setProgram)
      .catch((requestError) => {
        if (!(requestError instanceof ApiError && requestError.kind === 'aborted')) setError(requestError);
      });
    return () => controller.abort();
  }, [programId, requestVersion]);

  useEffect(() => {
    intelligenceController.current?.abort();
    intelligenceSequence.current += 1;
    setIntelligence(null);
    setIntelligenceError(false);
    setIntelligenceLoading(false);
    return () => {
      intelligenceController.current?.abort();
      intelligenceSequence.current += 1;
    };
  }, [programId]);

  const generateIntelligence = () => {
    if (!programId || intelligenceLoading) return;
    const request = intelligenceSequence.current + 1;
    intelligenceSequence.current = request;
    setIntelligenceLoading(true);
    setIntelligenceError(false);
    const controller = new AbortController();
    intelligenceController.current = controller;
    const activeProgramId = programId;
    getProgramIntelligence(programId, controller.signal)
      .then((result) => {
        if (request === intelligenceSequence.current && activeProgramId === programId) setIntelligence(result);
      })
      .catch((requestError) => {
        if (!(requestError instanceof ApiError && requestError.kind === 'aborted') && request === intelligenceSequence.current && activeProgramId === programId) setIntelligenceError(true);
      })
      .finally(() => {
        if (request === intelligenceSequence.current && activeProgramId === programId) setIntelligenceLoading(false);
      });
  };

  const retry = <Button variant="outlined" onClick={() => setRequestVersion((value) => value + 1)}>Retry</Button>;

  if (error instanceof ApiError && error.status === 404) {
    return <PageContainer><ErrorState title="Program not found." message="The requested program is not available." action={<Button component={RouterLink} to="/programs" variant="contained">Return to Programs</Button>} /></PageContainer>;
  }
  if (error) {
    return (
      <PageContainer><ErrorState
        title={error instanceof ApiError && error.kind === 'configuration' ? 'API configuration required' : 'Program could not be loaded'}
        message={error instanceof ApiError && error.kind === 'configuration' ? error.message : error instanceof ApiError && error.kind === 'network' ? 'Check your connection and confirm the API is running, then try again.' : 'The server could not load this program. Please try again.'}
        action={error instanceof ApiError && error.kind === 'configuration' ? undefined : retry}
      /></PageContainer>
    );
  }
  if (!program) return <PageContainer><LoadingState message="Loading program workspace" /></PageContainer>;

  const timeline = milestones(program);
  const actions = storedActions(program);
  const risks = storedRisks(program);
  const issues = storedIssues(program);
  const dependencies = storedDependencies(program);
  const decisions = storedDecisions(program);

  return (
    <PageContainer>
      <Stack spacing={{ xs: 4, md: 5 }}>
        <Paper component="header" variant="outlined" sx={{ p: { xs: 2.5, sm: 3.5 }, overflow: 'hidden' }}>
          <Typography variant="caption" color="text.secondary">Program Workspace</Typography>
          <Typography component="h1" variant="h1" sx={{ mt: 0.5, overflowWrap: 'anywhere' }}>
            {usableText(program.program_name) ?? 'Program name unavailable'}
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 0.75, overflowWrap: 'anywhere' }}>Program ID: {program.program_id}</Typography>
          <Grid2 container spacing={1.5} sx={{ mt: 2 }} data-testid="executive-header-status-grid">
            <Grid2 size={{ xs: 12, sm: 4 }}><StatusCard label="Current Phase" value={usableText(program.phase)} /></Grid2>
            <Grid2 size={{ xs: 12, sm: 4 }}><StatusCard label="Health" value={usableText(program.health)} /></Grid2>
            <Grid2 size={{ xs: 12, sm: 4 }}><StatusCard label="Confidence" value={usableText(program.confidence)} /></Grid2>
          </Grid2>
        </Paper>

        <WorkspaceSection title="Executive Summary">
          <Typography sx={{ maxWidth: 900, fontSize: '1.05rem', lineHeight: 1.7 }}>{executiveSummary(program)}</Typography>
        </WorkspaceSection>

        <WorkspaceSection title="Program Health" description="Reported program values; no composite score is calculated.">
          <Grid2 container spacing={1.5} data-testid="program-health-grid">
            <Grid2 size={{ xs: 12, md: 4 }}><StatusCard label="Current Phase" value={usableText(program.phase)} /></Grid2>
            <Grid2 size={{ xs: 12, md: 4 }}><StatusCard label="Health" value={usableText(program.health)} /></Grid2>
            <Grid2 size={{ xs: 12, md: 4 }}><StatusCard label="Confidence" value={usableText(program.confidence)} /></Grid2>
          </Grid2>
        </WorkspaceSection>

        <WorkspaceSection title="Project Overview">
          <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 } }}>
            <MetadataGrid items={[
              { label: 'Customer', value: usableText(program.customer) },
              { label: 'Description', value: usableText(program.description) },
              { label: 'Source', value: usableText(program.metadata?.source) },
              { label: 'Created', value: displayDate(program.metadata?.created_at) },
              { label: 'Last Updated', value: displayDate(program.metadata?.updated_at) },
            ]} />
          </Paper>
        </WorkspaceSection>

        <WorkspaceSection title="Timeline" description="Only milestones explicitly stored with the program are shown.">
          {timeline.length ? (
            <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 } }}>
              <Stack spacing={2.5} divider={<Divider />}>
                {timeline.map((milestone, index) => (
                  <Stack key={`${milestone.title}-${index}`} spacing={0.5}>
                    {milestone.date ? <Typography variant="caption" color="text.secondary">{displayDate(milestone.date)}</Typography> : null}
                    <Typography fontWeight={650}>{milestone.title}</Typography>
                    {milestone.description ? <Typography>{milestone.description}</Typography> : null}
                    {milestone.status ? <Typography variant="caption" color="text.secondary">Status: {milestone.status}</Typography> : null}
                  </Stack>
                ))}
              </Stack>
            </Paper>
          ) : (
            <Paper variant="outlined" sx={{ p: { xs: 3, sm: 4 }, textAlign: 'center', bgcolor: '#fafbfc' }}>
              <Typography fontWeight={650}>No milestones recorded</Typography>
              <Typography color="text.secondary" sx={{ mt: 0.5 }}>This program does not contain supported milestone records.</Typography>
            </Paper>
          )}
        </WorkspaceSection>

        <WorkspaceSection title="Stored Program Actions" description="Actions persisted with the program; generated intelligence remains separate and read-only.">
          <Stack spacing={1.5}>
                {actions.length ? actions.map((action) => (
                  <Paper key={action.object_id} variant="outlined" sx={{ p: 2 }}>
                    <Typography fontWeight={600}>{action.title}</Typography>
                    {[`Status: ${action.status}`, action.owner && `Owner: ${action.owner.display_name}`, action.due_date && `Due: ${action.due_date}`]
                      .filter(Boolean).map((detail) => <Typography key={detail} variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>{detail}</Typography>)}
                  </Paper>
                )) : <Typography color="text.secondary">No stored program actions are available.</Typography>}
          </Stack>
        </WorkspaceSection>

        <WorkspaceSection title="Stored Risks" description="Canonical risks explicitly persisted with the program.">
          <Stack spacing={1.5}>
            {risks.length ? risks.map((risk) => (
              <Paper key={risk.object_id} variant="outlined" sx={{ p: 2 }}>
                <Typography fontWeight={600}>{risk.title}</Typography>
                {[
                  `Status: ${risk.status}`,
                  risk.owner && `Owner: ${risk.owner.display_name}`,
                  risk.probability && `Probability: ${risk.probability}`,
                  risk.impact && `Impact: ${risk.impact}`,
                  risk.priority && `Priority: ${risk.priority}`,
                  risk.review_date && `Review date: ${risk.review_date}`,
                  risk.mitigation_plan && `Mitigation: ${risk.mitigation_plan}`,
                  risk.status === 'accepted' && risk.accepted_by && `Accepted by: ${risk.accepted_by.display_name}`,
                  risk.status === 'accepted' && risk.acceptance_rationale && `Acceptance rationale: ${risk.acceptance_rationale}`,
                ].filter(Boolean).map((detail) => <Typography key={String(detail)} variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>{detail}</Typography>)}
              </Paper>
            )) : <Typography color="text.secondary">No stored program risks are available.</Typography>}
          </Stack>
        </WorkspaceSection>

        <WorkspaceSection title="Stored Issues" description="Canonical issues explicitly persisted with the program.">
          <Stack spacing={1.5}>
            {issues.length ? issues.map((issue) => (
              <Paper key={issue.object_id} variant="outlined" sx={{ p: 2 }}>
                <Typography fontWeight={600}>{issue.title}</Typography>
                {[
                  `Status: ${issue.status}`,
                  issue.owner && `Owner: ${issue.owner.display_name}`,
                  issue.due_date && `Due date: ${issue.due_date}`,
                  issue.severity && `Severity: ${issue.severity}`,
                  issue.impact && `Impact: ${issue.impact}`,
                  issue.resolution_summary && `Resolution: ${issue.resolution_summary}`,
                  issue.resolved_at && `Resolved: ${issue.resolved_at}`,
                ].filter(Boolean).map((detail) => <Typography key={String(detail)} variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>{detail}</Typography>)}
              </Paper>
            )) : <Typography color="text.secondary">No stored program issues are available.</Typography>}
          </Stack>
        </WorkspaceSection>

        <WorkspaceSection title="Stored Dependencies" description="Canonical dependencies explicitly persisted with the program.">
          <Stack spacing={1.5}>
            {dependencies.length ? dependencies.map((dependency) => (
              <Paper key={dependency.object_id} variant="outlined" sx={{ p: 2 }}>
                <Typography fontWeight={600}>{dependency.title}</Typography>
                {[
                  `Status: ${dependency.status}`, `Type: ${dependency.dependency_type}`,
                  dependency.owner && `Owner: ${dependency.owner.display_name}`,
                  dependency.depends_on && `Depends on: ${dependency.depends_on}`,
                  dependency.external_party && `External party: ${dependency.external_party}`,
                  dependency.required_by_date && `Required by: ${dependency.required_by_date}`,
                  dependency.impact && `Impact: ${dependency.impact}`,
                  dependency.mitigation_plan && `Mitigation: ${dependency.mitigation_plan}`,
                ].filter(Boolean).map((detail) => <Typography key={String(detail)} variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>{detail}</Typography>)}
              </Paper>
            )) : <Typography color="text.secondary">No stored program dependencies are available.</Typography>}
          </Stack>
        </WorkspaceSection>

        <WorkspaceSection title="Decision Records" description="Canonical decisions explicitly persisted with the program; this view is read-only.">
          <Stack spacing={1.5}>
            {decisions.length ? decisions.map((decision) => (
              <Paper key={decision.object_id} variant="outlined" sx={{ p: 2 }}>
                <Typography fontWeight={600}>{decision.title}</Typography>
                {[
                  `Status: ${decision.status}`,
                  decision.decision && `Decision: ${decision.decision}`,
                  decision.rationale && `Rationale: ${decision.rationale}`,
                  decision.owner && `Owner: ${decision.owner.display_name}`,
                  decision.decision_date && `Decision date: ${decision.decision_date}`,
                  decision.review_date && `Review date: ${decision.review_date}`,
                  decision.impact && `Impact: ${decision.impact}`,
                  decision.alternatives_considered.length && `Alternatives considered: ${decision.alternatives_considered.join('; ')}`,
                ].filter(Boolean).map((detail) => <Typography key={String(detail)} variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>{detail}</Typography>)}
              </Paper>
            )) : <Typography color="text.secondary">No decision records are available.</Typography>}
          </Stack>
        </WorkspaceSection>

        <WorkspaceSection title="Intelligence" description="Generate current decision support on demand. Results are not persisted.">
          <Stack spacing={2}>
            <Box><Button variant={intelligence ? 'outlined' : 'contained'} disabled={intelligenceLoading} onClick={generateIntelligence}>
              {intelligenceLoading ? 'Generating Intelligence…' : intelligence ? 'Refresh Intelligence' : intelligenceError ? 'Retry Intelligence' : 'Generate Intelligence'}
            </Button></Box>
            {intelligenceLoading ? <LoadingState message="Generating workspace intelligence" /> : null}
            {intelligenceError && !intelligenceLoading ? (
              <ErrorState title="Intelligence is unavailable" message="The workspace remains available. Try generating intelligence again when the service is reachable." />
            ) : null}
            {!intelligence && !intelligenceLoading && !intelligenceError ? (
              <Paper variant="outlined" sx={{ p: 3, bgcolor: '#fafbfc' }}><Typography color="text.secondary">Intelligence has not been generated for this workspace session.</Typography></Paper>
            ) : null}
            {intelligence && !intelligenceLoading ? <IntelligenceResult intelligence={intelligence} /> : null}
          </Stack>
        </WorkspaceSection>
      </Stack>
    </PageContainer>
  );
}
