import CircleRoundedIcon from '@mui/icons-material/CircleRounded';
import { Chip, useTheme } from '@mui/material';

type Tone = 'healthy' | 'atRisk' | 'critical' | 'informational' | 'neutral';
interface BadgeValue { label: string; tone: Tone }

function key(value?: string | null) { return value?.trim().toLowerCase().replace(/[_-]+/g, ' ').replace(/\s+/g, ' ') ?? ''; }
function title(value: string) { return value.replace(/\b\w/g, (letter) => letter.toUpperCase()); }

function StatusBadge({ value, ariaLabel }: { value: BadgeValue; ariaLabel: string }) {
  const theme = useTheme();
  const tone = theme.palette.status[value.tone];
  return <Chip aria-label={`${ariaLabel}: ${value.label}`} icon={<CircleRoundedIcon />} label={value.label} size="small" variant="outlined" sx={{ color: tone.main, bgcolor: tone.subtle, borderColor: tone.border, '& .MuiChip-icon': { color: tone.main, fontSize: 8 } }} />;
}

export function HealthStatusBadge({ value }: { value?: string | null }) {
  const normalized = key(value);
  const display: BadgeValue = ['healthy', 'green'].includes(normalized) ? { label: 'Healthy', tone: 'healthy' }
    : ['on track', 'ontrack'].includes(normalized) ? { label: 'On Track', tone: 'healthy' }
      : ['at risk', 'yellow', 'amber', 'attention'].includes(normalized) ? { label: 'At Risk', tone: 'atRisk' }
        : ['critical', 'red'].includes(normalized) ? { label: 'Critical', tone: 'critical' }
          : { label: 'Unknown', tone: 'neutral' };
  return <StatusBadge value={display} ariaLabel="Health" />;
}

export function ConfidenceBadge({ value, contextual = false }: { value?: string | null; contextual?: boolean }) {
  const normalized = key(value);
  const label = ['high', 'medium', 'low'].includes(normalized) ? title(normalized) : 'Unknown';
  const theme = useTheme();
  const tone = theme.palette.confidence[label.toLowerCase() as 'high' | 'medium' | 'low'] ?? theme.palette.confidence.unknown;
  return <Chip aria-label={`Confidence: ${label}`} icon={<CircleRoundedIcon />} label={contextual ? `Confidence: ${label.toUpperCase()}` : label} size="small" variant="outlined" sx={{ color: tone.main, bgcolor: tone.subtle, borderColor: tone.border, '& .MuiChip-icon': { color: tone.main, fontSize: 8 } }} />;
}

export function PhaseBadge({ value }: { value?: string | null }) {
  const normalized = key(value);
  const labels: Record<string, string> = {
    initiation: 'Initiation', 'program initiation': 'Initiation', planning: 'Planning', execution: 'Execution', delivery: 'Execution',
    transition: 'Transition', 'transition handoff': 'Transition', hypercare: 'Hypercare', closed: 'Closed',
    'operations closure': 'Closed', discovery: 'Discovery', 'readiness go live': 'Readiness',
  };
  const label = labels[normalized] ?? 'Unknown';
  return <StatusBadge value={{ label, tone: label === 'Unknown' ? 'neutral' : 'informational' }} ariaLabel="Phase" />;
}

export function SeverityBadge({ value }: { value?: string | null }) {
  const normalized = key(value);
  const tones: Record<string, Tone> = { critical: 'critical', high: 'critical', medium: 'atRisk', low: 'neutral' };
  return <StatusBadge value={{ label: tones[normalized] ? title(normalized) : 'Unknown', tone: tones[normalized] ?? 'neutral' }} ariaLabel="Severity" />;
}
