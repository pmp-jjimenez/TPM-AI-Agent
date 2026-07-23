import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined';
import CheckCircleOutlineRoundedIcon from '@mui/icons-material/CheckCircleOutlineRounded';
import { Box, Button, Card, CardContent, Divider, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { MetricDisplay, SectionHeader, Surface } from '../../components/ui/Primitives';
import { ConfidenceBadge, HealthStatusBadge, PhaseBadge } from '../../components/ui/StatusBadges';
import type { ProgramRecord } from './programTypes';
import { usableText } from './programTypes';

export function DashboardSection({ title, action, children }: { title: string; action?: ReactNode; children: ReactNode }) {
  return (
    <Box component="section">
      <Box sx={{ mb: { xs: 2, md: 2.25 } }}><SectionHeader title={title} action={action} /></Box>
      {children}
    </Box>
  );
}

export function SummaryCard({ icon, metric, label }: { icon: ReactNode; metric: string | number; label: string }) {
  return (
    <Card component="article" aria-label={`${label}: ${metric}`} variant="outlined" sx={{ height: '100%', boxShadow: '0 1px 2px rgba(23, 37, 43, 0.03)', transition: 'border-color 120ms ease, box-shadow 120ms ease', '&:hover': { borderColor: 'border.strong', boxShadow: 1 } }}>
      <CardContent sx={{ p: { xs: 2.25, md: 2.5 }, '&:last-child': { pb: { xs: 2.25, md: 2.5 } } }}>
        <MetricDisplay value={metric} label={label} icon={<Box sx={{ display: 'grid', placeItems: 'center', width: 32, height: 32, borderRadius: 1, bgcolor: 'surface.sunken', color: 'text.muted', flexShrink: 0, '& .MuiSvgIcon-root': { fontSize: 18 } }}>{icon}</Box>} />
      </CardContent>
    </Card>
  );
}

const focusItems = [
  { title: 'Dependency approved', detail: 'A delivery dependency is ready for the next program review.' },
  { title: 'Risk increased', detail: 'Review changes to portfolio exposure and confirm ownership.' },
  { title: 'Decision recorded', detail: 'A new program decision is available for stakeholder awareness.' },
  { title: 'Executive review due', detail: 'Prepare the latest program narrative and decisions required.' },
];

export function FocusCard() {
  return (
    <Card variant="outlined" sx={{ height: '100%', boxShadow: '0 1px 2px rgba(23, 37, 43, 0.03)' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3.25 }, '&:last-child': { pb: { xs: 2.5, md: 3.25 } } }}>
        <Typography component="h2" variant="sectionTitle">Today&apos;s Focus</Typography>
        <Typography variant="supporting" color="text.secondary" sx={{ display: 'block', mt: 0.5, mb: 2.25 }}>Priority signals for TPM review.</Typography>
        <Stack divider={<Divider flexItem />}>
          {focusItems.map((item) => (
            <Stack key={item.title} direction="row" spacing={1.5} sx={{ py: 1.625 }}>
              <CheckCircleOutlineRoundedIcon sx={{ mt: 0.25, fontSize: 18, color: 'text.muted' }} />
              <Box>
                <Typography variant="cardTitle">{item.title}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.25 }}>{item.detail}</Typography>
              </Box>
            </Stack>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}

export function AIAdvisorCard() {
  return (
    <Card variant="outlined" sx={{ height: '100%', bgcolor: 'primary.light', borderColor: 'primary.light', borderLeft: '3px solid', borderLeftColor: 'primary.main', boxShadow: '0 1px 2px rgba(23, 37, 43, 0.03)' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3.25 }, '&:last-child': { pb: { xs: 2.5, md: 3.25 } }, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <Box sx={{ width: 30, height: 30, display: 'grid', placeItems: 'center', borderRadius: 1, bgcolor: 'background.paper', color: 'primary.main' }}><AutoAwesomeOutlinedIcon sx={{ fontSize: 17 }} /></Box>
            <Typography component="h2" variant="sectionTitle">AI Advisor</Typography>
          </Stack>
          <ConfidenceBadge value="High" contextual />
        </Stack>
        <Typography sx={{ mt: 3.25, fontSize: '1rem', lineHeight: 1.75, maxWidth: 560 }}>
          No critical blockers detected. Review open dependencies before the next executive review.
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 'auto', pt: 3 }}>
          Preview guidance only. Live AI analysis is not enabled.
        </Typography>
      </CardContent>
    </Card>
  );
}

export function ProgramPreviewCard({ program }: { program: ProgramRecord }) {
  const name = usableText(program.program_name) ?? '—';
  const updatedAt = usableText(program.metadata?.updated_at);
  return (
    <Surface component="article" sx={{ height: '100%', display: 'flex', flexDirection: 'column', transition: 'border-color 120ms ease, box-shadow 120ms ease', '&:hover': { borderColor: 'border.strong', boxShadow: 1 } }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 }, '&:last-child': { pb: { xs: 2.5, md: 3 } }, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Box>
          <Typography variant="overline" color="text.muted">Program</Typography>
          <Typography component="h3" variant="sectionTitle" sx={{ mt: 0.5, overflowWrap: 'anywhere' }}>{name}</Typography>
          <Typography variant="caption" color="text.muted" sx={{ display: 'block', mt: 0.5, overflowWrap: 'anywhere' }}>{program.program_id}</Typography>
        </Box>
        <Stack direction={{ xs: 'column', sm: 'row' }} gap={{ xs: 1.5, sm: 2 }} sx={{ mt: 2.5, mb: 2.5 }}>
          <Box sx={{ flex: 1 }}><Typography variant="metadata" color="text.muted" sx={{ display: 'block', mb: 0.75 }}>Current Phase</Typography><PhaseBadge value={usableText(program.phase)} /></Box>
          <Box sx={{ flex: 1 }}><Typography variant="metadata" color="text.muted" sx={{ display: 'block', mb: 0.75 }}>Health</Typography><HealthStatusBadge value={usableText(program.health)} /></Box>
          <Box sx={{ flex: 1 }}><Typography variant="metadata" color="text.muted" sx={{ display: 'block', mb: 0.75 }}>Confidence</Typography><ConfidenceBadge value={usableText(program.confidence)} /></Box>
        </Stack>
        <Box sx={{ pt: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="metadata" color="text.muted">Last Updated</Typography>
          <Typography variant="body2" sx={{ mt: 0.375 }}>{updatedAt ?? 'Not available'}</Typography>
        </Box>
        <Button
          component={RouterLink}
          to={`/programs/${encodeURIComponent(program.program_id)}`}
          size="small"
          endIcon={<ArrowForwardRoundedIcon />}
          sx={{ alignSelf: 'flex-start', mt: 2.5, px: 0 }}
          aria-label={`Open Program ${name}`}
        >
          Open Program
        </Button>
      </CardContent>
    </Surface>
  );
}
