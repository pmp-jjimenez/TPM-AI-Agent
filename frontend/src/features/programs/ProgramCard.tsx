import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';
import { Box, Card, CardActionArea, CardContent, Divider, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { ConfidenceBadge, HealthStatusBadge, PhaseBadge } from '../../components/ui/StatusBadges';
import type { ProgramRecord } from './programTypes';
import { usableText } from './programTypes';

export function ProgramCard({ program }: { program: ProgramRecord }) {
  const name = usableText(program.program_name);
  const updatedAt = usableText(program.metadata?.updated_at);

  return (
    <Card variant="outlined" sx={{ height: '100%', transition: 'border-color 120ms ease, box-shadow 120ms ease', '&:hover': { borderColor: 'border.strong', boxShadow: 1 } }}>
      <CardActionArea component={RouterLink} to={`/programs/${encodeURIComponent(program.program_id)}`}>
        <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
          <Typography variant="overline" color="text.muted">Program</Typography>
          <Typography component="h2" variant="sectionTitle" sx={{ mt: 0.5, overflowWrap: 'anywhere' }}>{name ?? '—'}</Typography>
          <Typography variant="caption" color="text.muted" sx={{ display: 'block', mt: 0.5 }}>{program.program_id}</Typography>
          <Stack direction="row" gap={1} flexWrap="wrap" sx={{ my: 2.5 }}>
            <PhaseBadge value={usableText(program.phase)} />
            <HealthStatusBadge value={usableText(program.health)} />
            <ConfidenceBadge value={usableText(program.confidence)} />
          </Stack>
          <Divider />
          <Stack direction="row" justifyContent="space-between" alignItems="flex-end" gap={2} sx={{ pt: 2 }}>
            <Box><Typography variant="metadata" color="text.muted">Last Updated</Typography><Typography variant="body2" sx={{ mt: 0.375 }}>{updatedAt ?? 'Not available'}</Typography></Box>
            <ArrowForwardRoundedIcon aria-hidden sx={{ fontSize: 18, color: 'primary.main' }} />
          </Stack>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
