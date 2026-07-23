import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@mui/material';
import { theme } from '../../app/theme';
import { ConfidenceBadge, HealthStatusBadge, PhaseBadge, SeverityBadge } from './StatusBadges';

function renderBadges() {
  render(<ThemeProvider theme={theme}><HealthStatusBadge value="green" /><HealthStatusBadge value="unexpected" /><ConfidenceBadge value="HIGH" /><ConfidenceBadge value="certain" /><PhaseBadge value="Program Initiation" /><PhaseBadge value="unmapped" /><SeverityBadge value="critical" /><SeverityBadge /></ThemeProvider>);
}

describe('operational status badges', () => {
  it('normalizes known values and exposes accessible text labels', () => {
    renderBadges();
    expect(screen.getByLabelText('Health: Healthy')).toHaveTextContent('Healthy');
    expect(screen.getByLabelText('Confidence: High')).toHaveTextContent('High');
    expect(screen.getByLabelText('Phase: Initiation')).toHaveTextContent('Initiation');
    expect(screen.getByLabelText('Severity: Critical')).toHaveTextContent('Critical');
  });

  it('uses a safe Unknown fallback for unsupported or missing display values', () => {
    renderBadges();
    expect(screen.getAllByText('Unknown')).toHaveLength(4);
  });
});
