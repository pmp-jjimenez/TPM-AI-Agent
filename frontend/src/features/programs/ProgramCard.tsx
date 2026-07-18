import { Card, CardActionArea, CardContent, Grid2, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import type { ProgramRecord } from './programTypes';
import { usableText } from './programTypes';

function Field({ label, value }: { label: string; value?: string }) {
  return (
    <Grid2 size={{ xs: 12, sm: 4 }}>
      <Typography variant="caption" color="text.secondary">{label}</Typography>
      <Typography sx={{ overflowWrap: 'anywhere' }}>{value ?? '—'}</Typography>
    </Grid2>
  );
}

export function ProgramCard({ program }: { program: ProgramRecord }) {
  const name = usableText(program.program_name);
  const updatedAt = usableText(program.metadata?.updated_at);

  return (
    <Card variant="outlined">
      <CardActionArea component={RouterLink} to={`/programs/${encodeURIComponent(program.program_id)}`}>
        <CardContent>
          <Typography component="h2" variant="h2" sx={{ mb: 2 }}>{name ?? '—'}</Typography>
          <Grid2 container spacing={2}>
            <Field label="Program ID" value={program.program_id} />
            <Field label="Current Phase" value={usableText(program.phase)} />
            <Field label="Last Updated" value={updatedAt} />
          </Grid2>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
