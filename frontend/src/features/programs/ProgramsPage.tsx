import AccountTreeOutlinedIcon from '@mui/icons-material/AccountTreeOutlined';
import CrisisAlertOutlinedIcon from '@mui/icons-material/CrisisAlertOutlined';
import ErrorOutlineOutlinedIcon from '@mui/icons-material/ErrorOutlineOutlined';
import FactCheckOutlinedIcon from '@mui/icons-material/FactCheckOutlined';
import FolderOpenOutlinedIcon from '@mui/icons-material/FolderOpenOutlined';
import HealthAndSafetyOutlinedIcon from '@mui/icons-material/HealthAndSafetyOutlined';
import TaskAltOutlinedIcon from '@mui/icons-material/TaskAltOutlined';
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined';
import { Button, Grid2, Stack, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { ApiError } from '../../api/client';
import { EmptyState } from '../../components/feedback/EmptyState';
import { ErrorState } from '../../components/feedback/ErrorState';
import { LoadingState } from '../../components/feedback/LoadingState';
import { PageContainer } from '../../components/layout/PageContainer';
import { getPrograms } from './programApi';
import { AIAdvisorCard, DashboardSection, FocusCard, ProgramPreviewCard, SummaryCard } from './CommandCenterComponents';
import type { ProgramRecord } from './programTypes';

function errorPresentation(error: unknown) {
  if (error instanceof ApiError && error.kind === 'configuration') return { title: 'API configuration required', message: error.message, retryable: false };
  if (error instanceof ApiError && error.kind === 'network') return { title: 'Programs are unavailable', message: 'Check your connection and confirm the API is running, then try again.', retryable: true };
  if (error instanceof ApiError && error.kind === 'malformed') return { title: 'Programs could not be loaded', message: 'The server returned an unexpected response. Please try again later.', retryable: true };
  return { title: 'Programs could not be loaded', message: 'The server could not load programs. Please try again.', retryable: true };
}

function greeting() {
  return new Date().getHours() < 12 ? 'Good Morning' : 'Good Afternoon';
}

function countItems(programs: ProgramRecord[], field: 'risks' | 'issues' | 'dependencies' | 'decisions' | 'next_actions', closed: Set<string>) {
  return programs.reduce((total, program) => total + (program[field] ?? []).filter((item) => !closed.has(item.status)).length, 0);
}

function portfolioHealth(programs: ProgramRecord[]) {
  const health = programs.map((program) => typeof program.health === 'string' ? program.health.trim() : '').filter(Boolean);
  if (!health.length) return '—';
  if (health.some((value) => ['red', 'critical'].includes(value.toLowerCase()))) return 'Critical';
  if (health.some((value) => ['yellow', 'amber', 'at risk'].includes(value.toLowerCase()))) return 'Attention';
  if (health.every((value) => value.toLowerCase() === 'green')) return 'Healthy';
  return 'Mixed';
}

export function ProgramsPage() {
  const [programs, setPrograms] = useState<ProgramRecord[] | null>(null);
  const [error, setError] = useState<unknown>();
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setPrograms(null);
    setError(undefined);
    getPrograms(controller.signal)
      .then((result) => setPrograms([...result].sort((a, b) => (a.program_name ?? '').localeCompare(b.program_name ?? '', undefined, { sensitivity: 'base' }))))
      .catch((requestError) => {
        if (!(requestError instanceof ApiError && requestError.kind === 'aborted')) setError(requestError);
      });
    return () => controller.abort();
  }, [requestVersion]);

  const presentation = error ? errorPresentation(error) : null;
  const metrics = programs ? [
    { label: 'Active Programs', metric: programs.length, icon: <FolderOpenOutlinedIcon /> },
    { label: 'Portfolio Health', metric: portfolioHealth(programs), icon: <HealthAndSafetyOutlinedIcon /> },
    { label: 'Open Risks', metric: countItems(programs, 'risks', new Set(['closed'])), icon: <WarningAmberOutlinedIcon /> },
    { label: 'Open Issues', metric: countItems(programs, 'issues', new Set(['resolved', 'closed'])), icon: <ErrorOutlineOutlinedIcon /> },
    { label: 'Dependencies', metric: countItems(programs, 'dependencies', new Set(['resolved', 'closed'])), icon: <AccountTreeOutlinedIcon /> },
    { label: 'Decision Records', metric: programs.reduce((total, program) => total + (program.decisions?.length ?? 0), 0), icon: <FactCheckOutlinedIcon /> },
    { label: 'Open Actions', metric: countItems(programs, 'next_actions', new Set(['completed', 'cancelled'])), icon: <TaskAltOutlinedIcon /> },
    { label: 'Major Incidents', metric: '—', icon: <CrisisAlertOutlinedIcon /> },
  ] : [];

  return (
    <PageContainer>
      <Stack spacing={{ xs: 4, md: 5 }}>
        <header>
          <Typography variant="pageEyebrow" color="text.muted">{greeting()}</Typography>
          <Typography component="h1" variant="pageTitle" sx={{ mt: 0.5 }}>TPM Command Center</Typography>
          <Typography variant="pageSubtitle" color="text.secondary" sx={{ mt: 0.75 }}>Manage complex enterprise programs with confidence.</Typography>
        </header>

        {presentation ? (
          <ErrorState title={presentation.title} message={presentation.message} action={presentation.retryable ? <Button variant="outlined" onClick={() => setRequestVersion((value) => value + 1)}>Retry</Button> : undefined} />
        ) : programs === null ? (
          <LoadingState message="Loading programs" />
        ) : (
          <>
            <DashboardSection title="Portfolio Summary">
              <Grid2 container spacing={1.5}>
                {metrics.map((metric) => <Grid2 key={metric.label} size={{ xs: 12, sm: 6, lg: 3 }}><SummaryCard {...metric} /></Grid2>)}
              </Grid2>
            </DashboardSection>

            <Grid2 container spacing={2}>
              <Grid2 size={{ xs: 12, lg: 7 }}><FocusCard /></Grid2>
              <Grid2 size={{ xs: 12, lg: 5 }}><AIAdvisorCard /></Grid2>
            </Grid2>

            <DashboardSection title="Active Programs">
              {programs.length === 0 ? (
                <EmptyState title="No programs available" description="No valid program records are currently available." />
              ) : (
                <Grid2 container spacing={2}>
                  {programs.slice(0, 3).map((program) => <Grid2 key={program.program_id} size={{ xs: 12, md: 6, xl: 4 }}><ProgramPreviewCard program={program} /></Grid2>)}
                </Grid2>
              )}
            </DashboardSection>
          </>
        )}
      </Stack>
    </PageContainer>
  );
}
