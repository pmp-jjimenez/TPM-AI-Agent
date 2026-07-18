import { Button, Divider, Grid2, Paper, Stack, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { ApiError } from '../../api/client';
import { ErrorState } from '../../components/feedback/ErrorState';
import { LoadingState } from '../../components/feedback/LoadingState';
import { PageContainer } from '../../components/layout/PageContainer';
import {
  MetadataGrid,
  MissingInformationCard,
  RecommendationCard,
  SectionHeader,
  StatusCard,
} from './ExecutiveWorkspaceComponents';
import { getProgram } from './programApi';
import type { ProgramRecord } from './programTypes';
import { usableText } from './programTypes';

interface Milestone { date?: string; title: string; description?: string; status?: string }
interface StoredAction { description: string; status?: string; owner?: string; dueDate?: string }

const completenessFields = [
  ['Sponsor', 'sponsor'],
  ['Budget', 'budget'],
  ['Target Go-Live', 'target_go_live'],
  ['Architecture', 'architecture'],
  ['Dependencies', 'dependencies'],
  ['Governance', 'governance'],
] as const;

function hasUsableValue(value: unknown): boolean {
  if (typeof value === 'string') return Boolean(value.trim());
  if (typeof value === 'number') return Number.isFinite(value);
  if (typeof value === 'boolean') return true;
  if (Array.isArray(value)) return value.some(hasUsableValue);
  if (value && typeof value === 'object') return Object.values(value).some(hasUsableValue);
  return false;
}

function missingInformation(program: ProgramRecord): string[] {
  return completenessFields
    .filter(([, field]) => !hasUsableValue(program[field]))
    .map(([label]) => label);
}

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

function storedActions(program: ProgramRecord): StoredAction[] {
  return (program.next_actions ?? []).flatMap((entry) => {
    if (typeof entry === 'string') return entry.trim() ? [{ description: entry.trim() }] : [];
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) return [];
    const record = entry as Record<string, unknown>;
    const description = usableText(record.description) ?? usableText(record.action) ?? usableText(record.title) ?? usableText(record.name);
    if (!description) return [];
    return [{
      description,
      status: usableText(record.status),
      owner: usableText(record.owner),
      dueDate: usableText(record.due_date),
    }];
  });
}

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

  const missing = missingInformation(program);
  const timeline = milestones(program);
  const actions = storedActions(program);
  const initiation = usableText(program.phase)?.toLowerCase() === 'program initiation';

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

        <WorkspaceSection title="Missing Information" description="A completeness check of executive program context.">
          <MissingInformationCard fields={missing} />
        </WorkspaceSection>

        <WorkspaceSection title="Next Steps" description="Stored program actions are separated from deterministic workspace recommendations.">
          <Grid2 container spacing={2}>
            <Grid2 size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.5}>
                <Typography component="h3" fontWeight={650}>Stored Program Actions</Typography>
                {actions.length ? actions.map((action, index) => (
                  <Paper key={`${action.description}-${index}`} variant="outlined" sx={{ p: 2 }}>
                    <Typography fontWeight={600}>{action.description}</Typography>
                    {[action.status && `Status: ${action.status}`, action.owner && `Owner: ${action.owner}`, action.dueDate && `Due: ${action.dueDate}`]
                      .filter(Boolean).map((detail) => <Typography key={detail} variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>{detail}</Typography>)}
                  </Paper>
                )) : <Typography color="text.secondary">No stored program actions are available.</Typography>}
              </Stack>
            </Grid2>
            <Grid2 size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.5}>
                <Typography component="h3" fontWeight={650}>Workspace Recommendations</Typography>
                {initiation ? <RecommendationCard title="Internal Technical Kickoff" description="Recommended because the current phase is Program Initiation." /> : null}
                {missing.length ? <RecommendationCard title="Collect executive program information" description={`Collect: ${missing.join(', ')}.`} /> : null}
                {!initiation && !missing.length ? <Typography color="text.secondary">No deterministic recommendations apply.</Typography> : null}
              </Stack>
            </Grid2>
          </Grid2>
        </WorkspaceSection>
      </Stack>
    </PageContainer>
  );
}
