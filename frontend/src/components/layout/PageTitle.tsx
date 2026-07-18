import { Box, Typography } from '@mui/material';

interface PageTitleProps {
  title: string;
  description?: string;
}

export function PageTitle({ title, description }: PageTitleProps) {
  return (
    <Box component="header" sx={{ mb: 3 }}>
      <Typography component="h1" variant="h1">{title}</Typography>
      {description && (
        <Typography color="text.secondary" sx={{ mt: 0.75, maxWidth: 720 }}>
          {description}
        </Typography>
      )}
    </Box>
  );
}
