import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#1d4ed8', dark: '#1e3a8a' },
    background: { default: '#f6f7f9', paper: '#ffffff' },
    text: { primary: '#172033', secondary: '#5f6b7a' },
    divider: '#dfe3e8',
  },
  shape: { borderRadius: 8 },
  typography: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    h1: { fontSize: '1.75rem', lineHeight: 1.25, fontWeight: 650, letterSpacing: '-0.02em' },
    h2: { fontSize: '1.25rem', lineHeight: 1.35, fontWeight: 650 },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  components: {
    MuiButtonBase: { defaultProps: { disableRipple: true } },
    MuiPaper: { defaultProps: { elevation: 0 } },
  },
});
