import { Box, Chip, Grid2, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';
import { ConfidenceBadge, HealthStatusBadge, PhaseBadge } from '../../components/ui/StatusBadges';
import { MetadataList, MetricDisplay, SectionHeader, Surface } from '../../components/ui/Primitives';

export interface MissionHeaderProps {
  name: string;
  description?: string;
  programId: string;
  phase?: string;
  health?: string;
  confidence?: string;
  updatedAt?: string;
}

export function MissionHeader({ name, description, programId, phase, health, confidence, updatedAt }: MissionHeaderProps) {
  return (
    <Surface component="header" sx={{ position: 'relative', overflow: 'hidden', p: { xs: 2.5, sm: 4 }, borderTop: '4px solid', borderTopColor: 'primary.main' }}>
      <Box aria-hidden sx={{ position: 'absolute', width: 240, height: 240, borderRadius: '50%', bgcolor: 'primary.light', opacity: 0.45, right: -100, top: -130 }} />
      <Stack spacing={2.5} sx={{ position: 'relative' }}>
        <Box>
          <Typography variant="pageEyebrow" color="primary.main">Program Mission Control</Typography>
          <Typography component="h1" variant="pageTitle" sx={{ mt: 0.75, overflowWrap: 'anywhere', maxWidth: 860 }}>{name}</Typography>
          <Typography variant="pageSubtitle" color="text.secondary" sx={{ mt: 1, maxWidth: 760, overflowWrap: 'anywhere' }}>
            {description ?? 'No program description is available.'}
          </Typography>
        </Box>
        <Stack direction="row" gap={1} flexWrap="wrap" alignItems="center">
          <PhaseBadge value={phase} />
          <HealthStatusBadge value={health} />
          <ConfidenceBadge value={confidence} />
        </Stack>
        <Stack direction={{ xs: 'column', sm: 'row' }} gap={{ xs: 0.5, sm: 2 }}>
          <Typography variant="metadata" color="text.muted">Program ID: {programId}</Typography>
          <Typography variant="metadata" color="text.muted">Last updated: {updatedAt ?? 'Not available'}</Typography>
        </Stack>
      </Stack>
    </Surface>
  );
}

export function ExecutiveMetricCard({ label, value, supportingText }: { label: string; value: ReactNode; supportingText?: string }) {
  return (
    <Surface component="article" aria-label={label} sx={{ p: 2.25, height: '100%' }}>
      <MetricDisplay label={label} value={value as string | number} />
      {supportingText ? <Typography variant="supporting" color="text.muted" sx={{ display: 'block', mt: 1.25 }}>{supportingText}</Typography> : null}
    </Surface>
  );
}

export type PriorityTone = 'critical' | 'attention' | 'clear' | 'neutral';
export interface PriorityItem { id: string; title: string; detail: string; tone: PriorityTone }

const priorityTone = {
  critical: { color: 'status.critical.foreground', bgcolor: 'status.critical.background', borderColor: 'status.critical.border' },
  attention: { color: 'status.atRisk.foreground', bgcolor: 'status.atRisk.background', borderColor: 'status.atRisk.border' },
  clear: { color: 'status.healthy.foreground', bgcolor: 'status.healthy.background', borderColor: 'status.healthy.border' },
  neutral: { color: 'status.neutral.foreground', bgcolor: 'status.neutral.background', borderColor: 'status.neutral.border' },
} as const;

export function PriorityCard({ items }: { items: PriorityItem[] }) {
  return (
    <Surface component="section" aria-label="Today's Priorities" sx={{ p: { xs: 2.25, sm: 3 }, height: '100%' }}>
      <SectionHeader title="Today's Priorities" description="Signals derived from current program records." />
      <Stack spacing={1.25} sx={{ mt: 2.25 }}>
        {items.map((item) => (
          <Stack key={item.id} direction="row" gap={1.5} alignItems="flex-start" sx={{ p: 1.5, border: '1px solid', borderRadius: 1.25, ...priorityTone[item.tone] }}>
            <Box aria-hidden sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'currentColor', mt: 0.75, flexShrink: 0 }} />
            <Box><Typography variant="cardTitle">{item.title}</Typography><Typography variant="supporting" sx={{ display: 'block', mt: 0.25, opacity: 0.86 }}>{item.detail}</Typography></Box>
          </Stack>
        ))}
      </Stack>
    </Surface>
  );
}

export function AIAssessmentCard() {
  return (
    <Surface component="section" aria-labelledby="ai-assessment-title" sx={{ p: { xs: 2.25, sm: 3 }, height: '100%', bgcolor: 'primary.light', borderColor: 'primary.main' }}>
      <Stack direction="row" justifyContent="space-between" gap={2} alignItems="flex-start">
        <Box><Typography variant="pageEyebrow" color="primary.main">AI Advisor</Typography><Typography id="ai-assessment-title" component="h2" variant="sectionTitle" sx={{ mt: 0.5 }}>AI Assessment</Typography></Box>
        <Chip label="Not generated" size="small" variant="outlined" />
      </Stack>
      <MetadataList items={[
        { label: 'Overall Assessment', value: 'Awaiting grounded program intelligence' },
        { label: 'Recommended Next Action', value: 'No recommendation available' },
        { label: 'Primary Watch Item', value: 'No watch item identified' },
        { label: 'Confidence', value: <ConfidenceBadge /> },
      ]} />
      <Typography variant="caption" color="text.muted" sx={{ display: 'block', mt: 1.5 }}>AI guidance is intentionally unavailable until a grounded assessment is provided.</Typography>
    </Surface>
  );
}

export interface OperationalItem {
  id: string;
  title: string;
  status: string;
  badge?: ReactNode;
  details: Array<{ label: string; value?: string | null }>;
}

export function OperationalItemCard({ item }: { item: OperationalItem }) {
  return (
    <Surface component="article" aria-label={item.title} sx={{ p: 2, height: '100%', '&:hover': { borderColor: 'border.strong' } }}>
      <Stack direction="row" justifyContent="space-between" gap={1.5} alignItems="flex-start">
        <Typography component="h3" variant="cardTitle" sx={{ overflowWrap: 'anywhere' }}>{item.title}</Typography>
        {item.badge ?? <Chip label={item.status.replaceAll('_', ' ')} size="small" variant="outlined" sx={{ textTransform: 'capitalize', flexShrink: 0 }} />}
      </Stack>
      <MetadataList items={item.details.filter((detail) => detail.value).map((detail) => ({ label: detail.label, value: detail.value }))} />
    </Surface>
  );
}

export function OperationalSection({ title, description, items, emptyMessage }: { title: string; description: string; items: OperationalItem[]; emptyMessage: string }) {
  return (
    <Stack component="section" spacing={2} aria-label={title}>
      <SectionHeader title={title} description={description} action={<Chip label={`${items.length} ${items.length === 1 ? 'record' : 'records'}`} size="small" variant="outlined" aria-label={`${title}: ${items.length} records`} />} />
      {items.length ? (
        <Grid2 container spacing={1.5}>
          {items.map((item) => <Grid2 key={item.id} size={{ xs: 12, lg: 6 }}><OperationalItemCard item={item} /></Grid2>)}
        </Grid2>
      ) : (
        <Surface sx={{ p: { xs: 2.5, sm: 3 }, bgcolor: 'background.subtle', textAlign: 'center' }}>
          <Typography variant="cardTitle">No {title.toLowerCase()} recorded</Typography>
          <Typography variant="supporting" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>{emptyMessage}</Typography>
        </Surface>
      )}
    </Stack>
  );
}
