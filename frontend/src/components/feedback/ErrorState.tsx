import ErrorOutlineRoundedIcon from '@mui/icons-material/ErrorOutlineRounded';
import { Alert, AlertTitle } from '@mui/material';

interface ErrorStateProps {
  title?: string;
  message: string;
}

export function ErrorState({ title = 'Something went wrong', message }: ErrorStateProps) {
  return (
    <Alert severity="error" icon={<ErrorOutlineRoundedIcon />} variant="outlined">
      <AlertTitle>{title}</AlertTitle>
      {message}
    </Alert>
  );
}
