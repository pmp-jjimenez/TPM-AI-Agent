import { Button, Chip, Divider, Stack, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink, useParams } from 'react-router-dom';
import { ApiError } from '../../api/client';
import { EmptyState } from '../../components/feedback/EmptyState';
import { ErrorState } from '../../components/feedback/ErrorState';
import { LoadingState } from '../../components/feedback/LoadingState';
import { PageContainer } from '../../components/layout/PageContainer';
import { PageTitle } from '../../components/layout/PageTitle';
import { getProgram } from './programApi';
import { MetadataField, SectionCard } from './SectionCard';
import type { ProgramRecord } from './programTypes';
import { usableText } from './programTypes';

interface TimelineEntry { date?: string; title?: string; description?: string }

function timelineEntries(program: ProgramRecord): TimelineEntry[] {
  return (program.meeting_history ?? []).flatMap((entry) => {
    if (!entry || typeof entry !== 'object' || Array.isArray(entry)) return [];
    const record = entry as Record<string, unknown>;
    const date = usableText(record.date) ?? usableText(record.timestamp) ?? usableText(record.occurred_at);
    const title = usableText(record.title) ?? usableText(record.summary);
    const description = usableText(record.description);
    return date || title || description ? [{ date, title, description }] : [];
  });
}

function missingFields(program: ProgramRecord): string[] {
  return [
    ['Program name', program.program_name],
    ['Description', program.description],
    ['Customer', program.customer],
    ['Current phase', program.phase],
    ['Health', program.health],
    ['Confidence', program.confidence],
    ['Last updated', program.metadata?.updated_at],
  ].filter(([, value]) => !usableText(value)).map(([label]) => label as string);
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

  return (
    <PageContainer>
      <PageTitle title={usableText(program?.program_name) ?? 'Program Workspace'} />
      {error instanceof ApiError && error.status === 404 ? (
        <ErrorState title="Program not found." message="The requested program is not available." action={<Button component={RouterLink} to="/programs" variant="contained">Return to Programs</Button>} />
      ) : error ? (
        <ErrorState
          title={error instanceof ApiError && error.kind === 'configuration' ? 'API configuration required' : 'Program could not be loaded'}
          message={error instanceof ApiError && error.kind === 'configuration' ? error.message : error instanceof ApiError && error.kind === 'network' ? 'Check your connection and confirm the API is running, then try again.' : 'The server could not load this program. Please try again.'}
          action={error instanceof ApiError && error.kind === 'configuration' ? undefined : retry}
        />
      ) : !program ? <LoadingState message="Loading program workspace" /> : (
        <Stack spacing={3}>
          <SectionCard title="Program">
            <MetadataField label="Program Name" value={usableText(program.program_name)} />
            <MetadataField label="Program ID" value={program.program_id} />
            <MetadataField label="Description" value={usableText(program.description)} />
            <MetadataField label="Customer" value={usableText(program.customer)} />
          </SectionCard>
          <SectionCard title="Status">
            <MetadataField label="Current Phase" value={usableText(program.phase)} />
            <MetadataField label="Health" value={usableText(program.health)} />
            <MetadataField label="Confidence" value={usableText(program.confidence)} />
            <Divider />
            <MetadataField label="Created" value={usableText(program.metadata?.created_at)} />
            <MetadataField label="Last Updated" value={usableText(program.metadata?.updated_at)} />
          </SectionCard>
          <SectionCard title="Timeline">
            {timelineEntries(program).length ? timelineEntries(program).map((entry, index) => (
              <Stack key={`${entry.date ?? ''}-${entry.title ?? ''}-${index}`} spacing={0.5}>
                {entry.date ? <Typography variant="caption" color="text.secondary">{entry.date}</Typography> : null}
                {entry.title ? <Typography fontWeight={600}>{entry.title}</Typography> : null}
                {entry.description ? <Typography>{entry.description}</Typography> : null}
              </Stack>
            )) : <Typography color="text.secondary">No supported timeline entries are available.</Typography>}
          </SectionCard>
          <SectionCard title="Missing Information">
            {missingFields(program).length ? (
              <Stack direction="row" gap={1} flexWrap="wrap">{missingFields(program).map((field) => <Chip key={field} label={field} variant="outlined" />)}</Stack>
            ) : <Typography color="text.secondary">No missing information was identified among the displayed fields.</Typography>}
          </SectionCard>
        </Stack>
      )}
    </PageContainer>
  );
}
