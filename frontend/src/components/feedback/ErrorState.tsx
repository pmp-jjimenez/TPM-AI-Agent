import ErrorOutlineRoundedIcon from '@mui/icons-material/ErrorOutlineRounded';
import { Alert, AlertTitle, Box } from '@mui/material';
import type { ReactNode } from 'react';

interface ErrorStateProps {
  title?: string;
  message: string;
  action?: ReactNode;
}

export function ErrorState({ title = 'Something went wrong', message, action }: ErrorStateProps) {
  return (
    <Alert severity="error" icon={<ErrorOutlineRoundedIcon />} variant="outlined">
      <AlertTitle>{title}</AlertTitle>
      {message}
      {action ? <Box sx={{ mt: 2 }}>{action}</Box> : null}
    </Alert>
  );
}
