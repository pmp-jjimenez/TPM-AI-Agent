import { CircularProgress, Stack, Typography } from '@mui/material';

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Loading' }: LoadingStateProps) {
  return (
    <Stack role="status" alignItems="center" spacing={2} sx={{ py: 8 }}>
      <CircularProgress size={28} />
      <Typography color="text.secondary">{message}</Typography>
    </Stack>
  );
}
