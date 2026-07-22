import { Box, Chip, Grid2, Paper, Stack, Typography } from '@mui/material';
import type { ReactNode } from 'react';
import type { IntelligenceResponse } from './programTypes';

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

function IntelligenceList({ items, empty }: { items: string[]; empty: string }) {
  return items.length ? (
    <Stack component="ul" spacing={0.75} sx={{ m: 0, pl: 2.5 }}>
      {items.map((item, index) => <Typography component="li" key={`${item}-${index}`}>{item}</Typography>)}
    </Stack>
  ) : <Typography color="text.secondary">{empty}</Typography>;
}

function EvidenceRefs({ refs }: { refs: string[] }) {
  return refs.length ? <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>Evidence: {refs.join(', ')}</Typography> : null;
}

export function IntelligenceResult({ intelligence }: { intelligence: IntelligenceResponse }) {
  const fallback = intelligence.source === 'deterministic_fallback';
  const categoryLabels = { fact: 'Facts', missing_information: 'Missing Information', assumption: 'Assumptions', risk: 'Risks', dependency: 'Dependencies', conflict: 'Conflicts' } as const;
  return (
    <Stack spacing={2.5}>
      <Stack direction={{ xs: 'column', sm: 'row' }} gap={1} alignItems={{ sm: 'center' }}>
        <Chip label={fallback ? 'Deterministic Fallback' : 'AI'} color={fallback ? 'warning' : 'primary'} variant={fallback ? 'outlined' : 'filled'} />
        <Typography variant="caption" color="text.secondary">Generated intelligence is read-only and is not persisted.</Typography>
      </Stack>
      <Paper variant="outlined" sx={{ p: { xs: 2, sm: 2.5 } }}>
        <MetadataGrid items={[
          { label: 'Primary Persona', value: intelligence.routing.primary_persona.display_name },
          { label: 'Supporting Personas', value: intelligence.routing.supporting_personas.map((persona) => persona.display_name).join(', ') || 'None' },
          { label: 'Confidence', value: intelligence.confidence },
          { label: 'Schema Version', value: intelligence.schema_version },
          { label: 'Generated', value: new Date(intelligence.generated_at).toLocaleString() },
        ]} />
      </Paper>
      <Box><Typography component="h3" fontWeight={650}>Summary</Typography><Typography sx={{ mt: 0.75 }}>{intelligence.summary || 'No grounded summary is available.'}</Typography></Box>
      <Paper variant="outlined" sx={{ p: 2.5, borderLeft: '4px solid', borderLeftColor: 'primary.main' }}>
        <Stack direction="row" justifyContent="space-between" gap={2}><Typography component="h3" fontWeight={700}>Next Action</Typography><Chip label={intelligence.next_action.priority} size="small" color="primary" /></Stack>
        <Typography sx={{ mt: 1, fontWeight: 650 }}>{intelligence.next_action.statement}</Typography>
        <Typography color="text.secondary" sx={{ mt: 0.5 }}>{intelligence.next_action.rationale}</Typography>
      </Paper>
      <Box><Typography component="h3" fontWeight={650} sx={{ mb: 1 }}>Findings</Typography>
      <Grid2 container spacing={2}>
        {Object.entries(categoryLabels).map(([category, title]) => {
          const items = intelligence.findings.filter((finding) => finding.category === category);
          return (
          <Grid2 key={title} size={{ xs: 12, md: 6 }}>
            <Paper variant="outlined" sx={{ p: 2, height: '100%' }}>
              <Typography component="h3" fontWeight={650} sx={{ mb: 1 }}>{title}</Typography>
              {items.length ? <Stack spacing={1.5}>{items.map((finding) => <Box key={finding.id}><Typography>{finding.statement}</Typography>{finding.impact ? <Typography color="text.secondary" sx={{ mt: 0.5 }}>{finding.impact}</Typography> : null}<Typography variant="caption" color="text.secondary">Confidence: {finding.confidence}</Typography><EvidenceRefs refs={finding.evidence_refs} /></Box>)}</Stack> : <Typography color="text.secondary">No {title.toLowerCase()} were identified.</Typography>}
            </Paper>
          </Grid2>
        )})}
      </Grid2>
      </Box>
      <Box><Typography component="h3" fontWeight={650} sx={{ mb: 1 }}>Recommendations</Typography>
        {intelligence.recommendations.length ? <Stack spacing={1.5}>{intelligence.recommendations.map((recommendation) => <Paper variant="outlined" sx={{ p: 2 }} key={recommendation.id}><Stack direction="row" justifyContent="space-between" gap={2}><Typography fontWeight={650}>{recommendation.statement}</Typography><Chip label={recommendation.priority} size="small" /></Stack><Typography color="text.secondary" sx={{ mt: 0.5 }}>{recommendation.rationale}</Typography><EvidenceRefs refs={recommendation.evidence_refs} /></Paper>)}</Stack> : <Typography color="text.secondary">No grounded recommendations were identified.</Typography>}
      </Box>
      <Box><Typography component="h3" fontWeight={650} sx={{ mb: 1 }}>Decisions Required</Typography>
        {intelligence.decisions_required.length ? <Stack spacing={1.5}>{intelligence.decisions_required.map((decision) => <Paper variant="outlined" sx={{ p: 2 }} key={decision.id}><Stack direction="row" justifyContent="space-between" gap={2}><Typography fontWeight={650}>{decision.statement}</Typography><Chip label={decision.priority} size="small" /></Stack><Typography color="text.secondary" sx={{ mt: 0.5 }}>{decision.reason}</Typography></Paper>)}</Stack> : <Typography color="text.secondary">No decisions are currently required.</Typography>}
      </Box>
      {intelligence.limitations.length ? (
        <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fafbfc' }}>
          <Typography component="h3" fontWeight={650} sx={{ mb: 1 }}>Limitations</Typography>
          <IntelligenceList items={intelligence.limitations} empty="No limitations were reported." />
        </Paper>
      ) : null}
    </Stack>
  );
}
