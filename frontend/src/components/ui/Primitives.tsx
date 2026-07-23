import { Box, Divider, Paper, Stack, Typography, type PaperProps } from '@mui/material';
import type { ReactNode } from 'react';

export function Surface({ children, sx, ...props }: PaperProps) {
  return <Paper variant="outlined" {...props} sx={{ borderRadius: 1.5, ...sx }}>{children}</Paper>;
}

export function SectionHeader({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
      <Box><Typography component="h2" variant="sectionTitle">{title}</Typography>{description ? <Typography variant="supporting" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>{description}</Typography> : null}</Box>
      {action}
    </Stack>
  );
}

export function MetricDisplay({ value, label, icon }: { value: string | number; label: string; icon?: ReactNode }) {
  return <Stack direction="row" justifyContent="space-between" spacing={2}><Box><Typography variant="metricValue">{value}</Typography><Typography variant="metricLabel" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>{label}</Typography></Box>{icon}</Stack>;
}

export interface MetadataItem { label: string; value?: ReactNode }
export function MetadataList({ items }: { items: MetadataItem[] }) {
  return <Stack divider={<Divider flexItem />}>{items.map((item) => <Stack key={item.label} direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" gap={0.5} sx={{ py: 1.25 }}><Typography variant="metadata" color="text.muted">{item.label}</Typography><Typography variant="body2" component="div" sx={{ overflowWrap: 'anywhere' }}>{item.value ?? '—'}</Typography></Stack>)}</Stack>;
}

export function SubtleDivider() { return <Divider sx={{ borderColor: 'border.subtle' }} />; }
