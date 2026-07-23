import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#2563eb', dark: '#1e40af', light: '#eff6ff' },
    background: { default: '#f7f8fa', paper: '#ffffff' },
    text: { primary: '#182230', secondary: '#667085' },
    divider: '#e4e7ec',
  },
  shape: { borderRadius: 8 },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h1: { fontSize: '1.625rem', lineHeight: 1.25, fontWeight: 700, letterSpacing: '-0.025em' },
    h2: { fontSize: '1.125rem', lineHeight: 1.4, fontWeight: 675, letterSpacing: '-0.01em' },
    h3: { fontSize: '1rem', lineHeight: 1.45, fontWeight: 650 },
    body1: { fontSize: '0.9375rem', lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', lineHeight: 1.55 },
    caption: { fontSize: '0.75rem', lineHeight: 1.5 },
    overline: { fontSize: '0.6875rem', lineHeight: 1.5, fontWeight: 700, letterSpacing: '0.08em' },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  components: {
    MuiButtonBase: { defaultProps: { disableRipple: true } },
    MuiPaper: {
      defaultProps: { elevation: 0 },
      styleOverrides: { outlined: { borderColor: '#e4e7ec' } },
    },
    MuiIconButton: { styleOverrides: { root: { borderRadius: 8 } } },
  },
});
