import { Box, Typography } from '@mui/material';

interface PageTitleProps {
  title: string;
  description?: string;
}

export function PageTitle({ title, description }: PageTitleProps) {
  return (
    <Box component="header" sx={{ mb: { xs: 2.5, md: 3.5 } }}>
      <Typography component="h1" variant="pageTitle">{title}</Typography>
      {description && (
        <Typography variant="pageSubtitle" color="text.secondary" sx={{ mt: 0.75, maxWidth: 720 }}>
          {description}
        </Typography>
      )}
    </Box>
  );
}
