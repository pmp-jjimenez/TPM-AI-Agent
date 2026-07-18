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
      sx={{ px: { xs: 3, sm: 6 }, py: { xs: 6, sm: 8 }, textAlign: 'center', bgcolor: 'background.paper' }}
    >
      <Box aria-hidden="true" sx={{ display: 'inline-flex', p: 1.5, mb: 2, borderRadius: 1.5, bgcolor: '#eef2f7', color: 'text.secondary', '& svg': { fontSize: 30 } }}>
        {icon}
      </Box>
      <Typography component="h2" variant="h2">{title}</Typography>
      <Typography color="text.secondary" sx={{ maxWidth: 580, mx: 'auto', mt: 1.25, lineHeight: 1.65 }}>
        {description}
      </Typography>
    </Paper>
  );
}
