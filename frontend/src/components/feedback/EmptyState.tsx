import InboxOutlinedIcon from '@mui/icons-material/InboxOutlined';
import { Box, Paper, Typography } from '@mui/material';
import type { ReactNode } from 'react';

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: ReactNode;
}

export function EmptyState({ title, description, icon = <InboxOutlinedIcon /> }: EmptyStateProps) {
  return (
    <Paper
      variant="outlined"
      sx={{ px: { xs: 3, sm: 6 }, py: { xs: 5, sm: 6 }, textAlign: 'center', bgcolor: 'background.subtle' }}
    >
      <Box aria-hidden="true" sx={{ display: 'inline-flex', p: 1.25, mb: 2, borderRadius: 1.5, bgcolor: 'surface.sunken', color: 'text.secondary', '& svg': { fontSize: 28 } }}>
        {icon}
      </Box>
      <Typography component="h2" variant="sectionTitle">{title}</Typography>
      <Typography variant="supporting" color="text.secondary" sx={{ display: 'block', maxWidth: 580, mx: 'auto', mt: 1.25 }}>
        {description}
      </Typography>
    </Paper>
  );
}
