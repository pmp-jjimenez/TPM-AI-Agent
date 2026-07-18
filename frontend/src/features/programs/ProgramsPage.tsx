import { Button, Stack } from '@mui/material';
import { useEffect, useState } from 'react';
import { ApiError } from '../../api/client';
import { EmptyState } from '../../components/feedback/EmptyState';
import { ErrorState } from '../../components/feedback/ErrorState';
import { LoadingState } from '../../components/feedback/LoadingState';
import { PageContainer } from '../../components/layout/PageContainer';
import { PageTitle } from '../../components/layout/PageTitle';
import { getPrograms } from './programApi';
import { ProgramCard } from './ProgramCard';
import type { ProgramRecord } from './programTypes';

function errorPresentation(error: unknown) {
  if (error instanceof ApiError && error.kind === 'configuration') {
    return { title: 'API configuration required', message: error.message, retryable: false };
  }
  if (error instanceof ApiError && error.kind === 'network') {
    return { title: 'Programs are unavailable', message: 'Check your connection and confirm the API is running, then try again.', retryable: true };
  }
  if (error instanceof ApiError && error.kind === 'malformed') {
    return { title: 'Programs could not be loaded', message: 'The server returned an unexpected response. Please try again later.', retryable: true };
  }
  return { title: 'Programs could not be loaded', message: 'The server could not load programs. Please try again.', retryable: true };
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

  return (
    <PageContainer>
      <PageTitle title="Programs" description="View and manage your program portfolio." />
      {presentation ? (
        <ErrorState
          title={presentation.title}
          message={presentation.message}
          action={presentation.retryable ? <Button variant="outlined" onClick={() => setRequestVersion((value) => value + 1)}>Retry</Button> : undefined}
        />
      ) : programs === null ? (
        <LoadingState message="Loading programs" />
      ) : programs.length === 0 ? (
        <EmptyState title="No programs available" description="No valid program records are currently available." />
      ) : (
        <Stack spacing={2}>{programs.map((program) => <ProgramCard key={program.program_id} program={program} />)}</Stack>
      )}
    </PageContainer>
  );
}
