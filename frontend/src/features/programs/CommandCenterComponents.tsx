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
      <Box sx={{ mb: 1.5 }}><SectionHeader title={title} action={action} /></Box>
      {children}
    </Box>
  );
}

export function SummaryCard({ icon, metric, label }: { icon: ReactNode; metric: string | number; label: string }) {
  return (
    <Card component="article" aria-label={`${label}: ${metric}`} variant="outlined" sx={{ height: '100%', transition: 'border-color 120ms ease', '&:hover': { borderColor: 'border.strong' } }}>
      <CardContent sx={{ p: 2.25, '&:last-child': { pb: 2.25 } }}>
        <MetricDisplay value={metric} label={label} icon={<Box sx={{ display: 'grid', placeItems: 'center', width: 36, height: 36, borderRadius: 1.25, bgcolor: 'primary.light', color: 'primary.main', flexShrink: 0 }}>{icon}</Box>} />
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
    <Card variant="outlined" sx={{ height: '100%' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 }, '&:last-child': { pb: { xs: 2.5, md: 3 } } }}>
        <Typography component="h2" variant="h2">Today&apos;s Focus</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 2 }}>Priority signals for TPM review.</Typography>
        <Stack divider={<Divider flexItem />}>
          {focusItems.map((item) => (
            <Stack key={item.title} direction="row" spacing={1.5} sx={{ py: 1.5 }}>
              <CheckCircleOutlineRoundedIcon sx={{ mt: 0.2, fontSize: 19, color: 'text.secondary' }} />
              <Box>
                <Typography fontWeight={650}>{item.title}</Typography>
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
    <Card variant="outlined" sx={{ height: '100%', bgcolor: 'background.subtle' }}>
      <CardContent sx={{ p: { xs: 2.5, md: 3 }, '&:last-child': { pb: { xs: 2.5, md: 3 } }, height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <AutoAwesomeOutlinedIcon color="primary" fontSize="small" />
            <Typography component="h2" variant="h2">AI Advisor</Typography>
          </Stack>
          <ConfidenceBadge value="High" contextual />
        </Stack>
        <Typography sx={{ mt: 3, fontSize: '1.05rem', lineHeight: 1.7, maxWidth: 560 }}>
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
  return (
    <Surface sx={{ height: '100%', display: 'flex', flexDirection: 'column', transition: 'border-color 120ms ease', '&:hover': { borderColor: 'border.strong' } }}>
      <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 }, display: 'flex', flexDirection: 'column', height: '100%' }}>
        <Typography component="h3" variant="cardTitle" sx={{ overflowWrap: 'anywhere' }}>{name}</Typography>
        <Stack direction="row" spacing={3} sx={{ mt: 2.25, mb: 2.5, flexWrap: 'wrap', rowGap: 1.5 }}>
          <PhaseBadge value={usableText(program.phase)} />
          <HealthStatusBadge value={usableText(program.health)} />
          <ConfidenceBadge value={usableText(program.confidence)} />
        </Stack>
        <Button
          component={RouterLink}
          to={`/programs/${encodeURIComponent(program.program_id)}`}
          size="small"
          endIcon={<ArrowForwardRoundedIcon />}
          sx={{ alignSelf: 'flex-start', mt: 'auto', px: 0 }}
          aria-label={`Open Program ${name}`}
        >
          Open Program
        </Button>
      </CardContent>
    </Surface>
  );
}
