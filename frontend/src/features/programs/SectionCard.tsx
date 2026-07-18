import { Paper, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

export function SectionCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Paper component="section" variant="outlined" sx={{ p: { xs: 2.5, sm: 3 } }}>
      <Typography component="h2" variant="h2" sx={{ mb: 2 }}>{title}</Typography>
      <Stack spacing={1.5}>{children}</Stack>
    </Paper>
  );
}

export function MetadataField({ label, value }: { label: string; value?: string }) {
  return (
    <div>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Typography sx={{ overflowWrap: 'anywhere' }}>{value ?? '—'}</Typography>
    </div>
  );
}
