import { Skeleton, Stack, Typography } from '@mui/material';

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Loading' }: LoadingStateProps) {
  return (
    <Stack role="status" alignItems="center" spacing={1.5} sx={{ py: 7 }}>
      <Skeleton variant="rounded" width={180} height={10} />
      <Skeleton variant="rounded" width={120} height={10} />
      <Typography variant="supporting" color="text.secondary" sx={{ mt: 1 }}>{message}</Typography>
    </Stack>
  );
}
