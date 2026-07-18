import { Box, Chip, Grid2, Paper, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';

export function SectionHeader({ title, description }: { title: string; description?: string }) {
  return (
    <Box>
      <Typography component="h2" variant="h2">{title}</Typography>
      {description ? <Typography color="text.secondary" sx={{ mt: 0.5 }}>{description}</Typography> : null}
    </Box>
  );
}

export function StatusCard({ label, value }: { label: string; value?: string }) {
  const uncertain = !value || value.toLowerCase() === 'unknown';
  return (
    <Paper variant="outlined" sx={{ height: '100%', p: 2, bgcolor: uncertain ? '#f8fafc' : 'background.paper' }}>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Typography sx={{ mt: 0.5, fontWeight: 650, color: uncertain ? 'text.secondary' : 'text.primary', overflowWrap: 'anywhere' }}>
        {value ?? '—'}
      </Typography>
    </Paper>
  );
}

export interface MetadataItem { label: string; value?: ReactNode }

export function MetadataGrid({ items }: { items: MetadataItem[] }) {
  return (
    <Grid2 container spacing={{ xs: 2, sm: 3 }}>
      {items.map(({ label, value }) => (
        <Grid2 key={label} size={{ xs: 12, sm: 6 }}>
          <Typography variant="caption" color="text.secondary">{label}</Typography>
          <Typography component="div" sx={{ mt: 0.25, lineHeight: 1.6, overflowWrap: 'anywhere', whiteSpace: 'pre-wrap' }}>
            {value ?? '—'}
          </Typography>
        </Grid2>
      ))}
    </Grid2>
  );
}

export function MissingInformationCard({ fields }: { fields: string[] }) {
  return (
    <Paper variant="outlined" sx={{ p: { xs: 2, sm: 2.5 }, bgcolor: '#fafbfc' }}>
      {fields.length ? (
        <>
          <Typography color="text.secondary" sx={{ mb: 1.5 }}>
            These details are not recorded. They are not risks or issues.
          </Typography>
          <Stack direction="row" gap={1} flexWrap="wrap">
            {fields.map((field) => <Chip key={field} label={field} size="small" variant="outlined" />)}
          </Stack>
        </>
      ) : <Typography color="text.secondary">All executive completeness fields are recorded.</Typography>}
    </Paper>
  );
}

export function RecommendationCard({ title, description }: { title: string; description: string }) {
  return (
    <Paper variant="outlined" sx={{ p: 2, borderLeft: '3px solid', borderLeftColor: 'primary.main' }}>
      <Typography fontWeight={650}>{title}</Typography>
      <Typography color="text.secondary" sx={{ mt: 0.5 }}>{description}</Typography>
    </Paper>
  );
}
